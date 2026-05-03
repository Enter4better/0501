from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import docker
import random
import json
from datetime import datetime
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.target import Target
from models.log import Log
from services.database import db_service
from services.async_queue import async_queue_service
from config import DOCKER_CONFIG

targets_bp = Blueprint('targets', __name__, url_prefix='/api/env')

def _find_free_port(start=8080, end=8999):
    import socket
    for port in range(start, end + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', port))
            s.close()
            return port
        except OSError:
            continue
    return None

def _cleanup_failed_containers():
    try:
        docker_client = docker.from_env()
        for c in docker_client.containers.list(all=True):
            if c.name and c.name.startswith(DOCKER_CONFIG['container_prefix']):
                if c.status in ('created', 'dead', 'exited'):
                    try:
                        c.remove(force=True)
                        current_app.logger.info(f"[CLEANUP] 移除残留容器: {c.name}")
                    except Exception as e:
                        current_app.logger.error(f"[CLEANUP] 移除 {c.name} 失败: {e}")
    except Exception as e:
        current_app.logger.error(f"[CLEANUP] 清理失败: {e}")

@targets_bp.route('/list', methods=['GET'])
def list_targets():
    try:
        user_id = 1
        targets = Target.list_all()
        
        docker_info = {}
        try:
            docker_client = docker.from_env()
            for container in docker_client.containers.list(all=True):
                if container.name.startswith(DOCKER_CONFIG['container_prefix']):
                    name = container.name
                    ports = ''
                    if container.ports:
                        port_list = []
                        for k, v in container.ports.items():
                            if v:
                                port_list.append(f"{v[0]['HostPort']}:{k}")
                        ports = ', '.join(port_list)
                    
                    docker_info[name] = {
                        'id': container.short_id,
                        'image': container.image.tags[0] if container.image.tags else container.image.short_id,
                        'status': container.status,
                        'ports': ports,
                        'created': datetime.fromtimestamp(container.attrs['Created']).strftime('%Y-%m-%d %H:%M') if 'Created' in container.attrs else 'N/A'
                    }
        except Exception as e:
            current_app.logger.error(f"获取Docker信息失败: {e}")
        
        result = []
        for target in targets:
            target_info = target.to_dict()
            if target.name in docker_info:
                target_info.update(docker_info[target.name])
            else:
                target_info.update({
                    'id': target.target_id,
                    'image': target.os,
                    'status': 'stopped',
                    'ports': target.port,
                    'created': target.created_at
                })
            # 确保所有字段都有默认值
            if 'image' not in target_info or not target_info['image']:
                target_info['image'] = target.os
            if 'ports' not in target_info or not target_info['ports']:
                target_info['ports'] = target.port
            if 'created' not in target_info or not target_info['created']:
                target_info['created'] = target.created_at
                
            result.append(target_info)
        
        return jsonify({'status': 'success', 'containers': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取靶场列表失败: {e}")
        # 即使出现异常，也返回成功状态和空列表，避免前端显示错误
        return jsonify({'status': 'success', 'containers': []}), 200

@targets_bp.route('/create', methods=['POST'])
# @jwt_required()  # 已移除令牌认证要求
def create_target():
    try:
        user_id = 1  # 默认用户ID，无需令牌认证
        data = request.get_json()
        
        required_fields = ['image', 'port']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'msg': f'{field} 是必填项'}), 400
        
        image = data.get('image')
        port_mapping = data.get('port')
        name = data.get('name', '')
        env_vars = data.get('env', '')
        
        _cleanup_failed_containers()
        
        # 自动生成唯一容器名称，即使传入name也加上时间戳防止冲突
        ts = datetime.now().strftime('%H%M%S')
        if not name:
            name = f'{DOCKER_CONFIG["container_prefix"]}{image.replace(":", "_").replace("/", "_")}_{ts}'
        else:
            # 传入自定义名称时也添加随机后缀避免重名冲突
            name = f'{DOCKER_CONFIG["container_prefix"]}{name}_{ts}'
        
        try:
            container_port = port_mapping.split(':')[1] if ':' in port_mapping else '80'
            host_port = int(port_mapping.split(':')[0]) if ':' in port_mapping else 8080
            
            assigned_port = None
            for attempt_port in [host_port] + list(range(8100, 8950, 50)):
                try:
                    docker_client = docker.from_env()
                    port_bindings = {f'{container_port}/tcp': ('127.0.0.1', attempt_port)}
                    env_list = [e.strip() for e in env_vars.split(',')] if env_vars else None
                    
                    container = docker_client.containers.run(
                        image, name=name, detach=True, ports=port_bindings,
                        environment=env_list, remove=False
                    )
                    assigned_port = attempt_port
                    break
                except Exception as port_err:
                    if 'port is already allocated' in str(port_err) or 'bind' in str(port_err).lower():
                        continue
                    else:
                        raise
            
            if assigned_port is None:
                return jsonify({'status': 'error', 'msg': '所有候选端口均被占用'}), 500
            
            import time
            time.sleep(1.5)
            container.reload()
            
            # 修复Target模型没有create方法的问题，使用构造函数+save
            target = Target(
                name=name,
                type='docker',
                port=f'{assigned_port}:{container_port}',
                os=image,
                status='running',
                config=json.dumps({
                    'image': image,
                    'host_port': assigned_port,
                    'container_port': container_port,
                    'environment': env_list
                })
            )
            target.save()
            if target:
                target.container_id = container.id
                target.update_status('running')
            
            Log.create('success', 'target', f'靶场创建成功: {name} (端口: {assigned_port})', 
                      details=f'target_id: {target.target_id}', user_id=user_id)
            
            return jsonify({
                'status': 'success',
                'container_id': container.short_id,
                'name': name,
                'port': assigned_port,
                'image': image,
                'container_port': container_port
            }), 201
            
        except docker.errors.NotFound:
            return jsonify({'status': 'error', 'msg': f'镜像 {image} 不存在'}), 400
        except docker.errors.APIError as e:
            return jsonify({'status': 'error', 'msg': f'Docker错误: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"创建靶场失败: {e}")
        return jsonify({'status': 'error', 'msg': '创建靶场失败'}), 500

@targets_bp.route('/start/<container_id>', methods=['POST'])
@jwt_required()
def start_target(container_id):
    try:
        user_id = get_jwt_identity()
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(container_id)
            container.start()
            
            target = Target.get_by_name(container.name)
            if target:
                target.update_status('running')
            
            Log.create('success', 'target', f'靶场启动成功: {container.name}', 
                      user_id=user_id, target_id=target.target_id if target else None)
            
            return jsonify({'status': 'success'}), 200
            
        except docker.errors.NotFound:
            return jsonify({'status': 'error', 'msg': '容器不存在'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"启动靶场失败: {e}")
        return jsonify({'status': 'error', 'msg': '启动靶场失败'}), 500

@targets_bp.route('/stop/<container_id>', methods=['POST'])
@jwt_required()
def stop_target(container_id):
    try:
        user_id = get_jwt_identity()
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(container_id)
            container.stop(timeout=10)
            
            target = Target.get_by_name(container.name)
            if target:
                target.update_status('stopped')
            
            Log.create('info', 'target', f'靶场停止成功: {container.name}', 
                      user_id=user_id, target_id=target.target_id if target else None)
            
            return jsonify({'status': 'success'}), 200
            
        except docker.errors.NotFound:
            return jsonify({'status': 'error', 'msg': '容器不存在'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"停止靶场失败: {e}")
        return jsonify({'status': 'error', 'msg': '停止靶场失败'}), 500

@targets_bp.route('/delete/<container_id>', methods=['POST'])
@jwt_required()
def delete_target(container_id):
    try:
        user_id = get_jwt_identity()
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(container_id)
            
            target = Target.get_by_name(container.name)
            
            try:
                container.stop(timeout=5)
            except Exception:
                pass
            
            container.remove(force=True)
            
            if target:
                target.delete()
            
            Log.create('info', 'target', f'靶场删除成功: {container.name}', 
                      user_id=user_id, target_id=target.target_id if target else None)
            
            return jsonify({'status': 'success', 'deleted': container_id}), 200
            
        except docker.errors.NotFound:
            return jsonify({'status': 'error', 'msg': '容器不存在'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"删除靶场失败: {e}")
        return jsonify({'status': 'error', 'msg': '删除靶场失败'}), 500

@targets_bp.route('/clean', methods=['POST'])
@jwt_required()
def clean_targets():
    try:
        user_id = get_jwt_identity()
        try:
            docker_client = docker.from_env()
            count = 0
            failed = []
            
            for c in docker_client.containers.list(all=True):
                if c.name and c.name.startswith(DOCKER_CONFIG['container_prefix']):
                    try:
                        c.remove(force=True)
                        count += 1
                        target = Target.get_by_name(c.name)
                        if target:
                            target.delete()
                    except Exception as e:
                        failed.append(f"{c.name}: {e}")
            
            Log.create('info', 'target', f'批量清理靶场成功: 清理了 {count} 个靶场', user_id=user_id)
            
            return jsonify({'status': 'success', 'cleaned': count, 'failed': failed}), 200
            
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"清理靶场失败: {e}")
        return jsonify({'status': 'error', 'msg': '清理靶场失败'}), 500

@targets_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_target_stats():
    try:
        user_id = get_jwt_identity()
        targets = Target.list_all()
        
        stats = {
            'total': len(targets),
            'running': len([t for t in targets if t.status == 'running']),
            'stopped': len([t for t in targets if t.status == 'stopped']),
            'created': len([t for t in targets if t.status == 'created'])
        }
        
        return jsonify({'status': 'success', 'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取靶场统计失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取靶场统计失败'}), 500

@targets_bp.route('/images', methods=['GET'])
@jwt_required()
def get_available_images():
    try:
        images = [
            {'value': 'nginx', 'label': 'Nginx Web服务器'},
            {'value': 'mysql:8.0', 'label': 'MySQL 8.0'},
            {'value': 'redis:alpine', 'label': 'Redis 缓存'},
            {'value': 'python:3.11-slim', 'label': 'Python 3.11'},
            {'value': 'ubuntu:22.04', 'label': 'Ubuntu 22.04'},
            {'value': 'metasploitable2', 'label': 'Metasploitable2'},
            {'value': 'dvwa', 'label': 'DVWA (漏洞靶场)'},
            {'value': 'wordpress:latest', 'label': 'WordPress'},
            {'value': 'php:8.1-apache', 'label': 'PHP 8.1 + Apache'},
            {'value': 'node:18-alpine', 'label': 'Node.js 18'}
        ]
        
        return jsonify({'status': 'success', 'images': images}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取镜像列表失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取镜像列表失败'}), 500

# 新增RESTful接口
@targets_bp.route('/<target_id>', methods=['GET'])
@jwt_required()
def get_target(target_id):
    """获取单个靶场详情"""
    try:
        user_id = get_jwt_identity()
        
        target = Target.get_by_id(target_id)
        if not target:
            return jsonify({'status': 'error', 'msg': '靶场不存在'}), 404
        
        if target.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '无权访问此靶场'}), 403
        
        result = target.to_dict()
        
        try:
            docker_client = docker.from_env()
            if target.name:
                container = docker_client.containers.get(target.name)
                result['container_id'] = container.short_id
                result['status'] = container.status
        except docker.errors.NotFound:
            result['status'] = 'stopped'
        except Exception as e:
            current_app.logger.error(f"获取Docker信息失败: {e}")
        
        return jsonify({'status': 'success', 'target': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取靶场详情失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取靶场详情失败'}), 500

@targets_bp.route('/<target_id>', methods=['PUT'])
@jwt_required()
def update_target(target_id):
    """更新靶场配置"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        target = Target.get_by_id(target_id)
        if not target:
            return jsonify({'status': 'error', 'msg': '靶场不存在'}), 404
        
        if target.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '无权修改此靶场'}), 403
        
        if 'name' in data:
            target.name = data['name']
        if 'description' in data:
            target.description = data['description']
        
        target.save()
        
        return jsonify({'status': 'success', 'msg': '靶场配置更新成功', 'target': target.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"更新靶场配置失败: {e}")
        return jsonify({'status': 'error', 'msg': '更新靶场配置失败'}), 500

@targets_bp.route('/restart/<container_id>', methods=['POST'])
@jwt_required()
def restart_target(container_id):
    """重启靶场"""
    try:
        user_id = get_jwt_identity()
        
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(container_id)
            container.restart(timeout=10)
            
            target = Target.get_by_name(container.name)
            if target:
                target.update_status('running')
            
            Log.create('info', 'target', f'靶场重启成功: {container.name}', 
                      user_id=user_id, target_id=target.target_id if target else None)
            
            return jsonify({'status': 'success'}), 200
            
        except docker.errors.NotFound:
            return jsonify({'status': 'error', 'msg': '容器不存在'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"重启靶场失败: {e}")
        return jsonify({'status': 'error', 'msg': '重启靶场失败'}), 500

@targets_bp.route('/<target_id>/status', methods=['GET'])
@jwt_required()
def get_target_status(target_id):
    """获取靶场运行状态"""
    try:
        user_id = get_jwt_identity()
        
        target = Target.get_by_id(target_id)
        if not target:
            return jsonify({'status': 'error', 'msg': '靶场不存在'}), 404
        
        if target.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '无权访问此靶场'}), 403
        
        status_info = {
            'target_id': target_id,
            'name': target.name,
            'status': target.status,
            'container_status': 'unknown'
        }
        
        try:
            docker_client = docker.from_env()
            if target.name:
                container = docker_client.containers.get(target.name)
                status_info['container_status'] = container.status
                status_info['status'] = container.status
        except docker.errors.NotFound:
            status_info['container_status'] = 'not_found'
            status_info['status'] = 'stopped'
        except Exception as e:
            current_app.logger.error(f"获取Docker状态失败: {e}")
        
        return jsonify({'status': 'success', 'data': status_info}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取靶场状态失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取靶场状态失败'}), 500