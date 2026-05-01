# -*- coding: utf-8 -*-
"""
环境管理Agent - 负责靶场底层的资源编排
"""
import docker
import subprocess
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import uuid

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.target import Target
from models.log import Log
from services.database import db_service

logger = logging.getLogger('agents.env_manager')


class EnvManagerAgent:
    """环境管理Agent - 负责靶场底层的资源编排"""
    
    def __init__(self):
        self.docker_client = None
        self._init_docker_client()
    
    def _init_docker_client(self):
        """初始化Docker客户端"""
        try:
            self.docker_client = docker.from_env()
            # 测试连接
            self.docker_client.ping()
            logger.info("Docker客户端初始化成功")
        except Exception as e:
            logger.error(f"Docker客户端初始化失败: {e}")
            self.docker_client = None
    
    def create_environment(self, scenario_description, user_id=None):
        """根据场景描述创建环境"""
        try:
            logger.info(f"开始创建环境: {scenario_description}")
            
            # 解析场景描述，确定需要的组件
            components = self._parse_scenario(scenario_description)
            
            # 创建目标环境记录
            target = Target(
                name=f"AI_Environment_{uuid.uuid4().hex[:8]}",
                type='container',
                ip='127.0.0.1',
                port=self._find_available_port(),
                os='Linux',
                status='creating',
                description=scenario_description,
                config=json.dumps(components)
            )
            target.save()
            
            # 记录日志
            Log.create('info', 'env_manager', f'开始创建环境: {target.name}', user_id=user_id)
            
            # 根据组件需求创建容器
            containers = self._create_containers(components, target.target_id)
            
            # 更新目标状态
            target.status = 'online'
            target.updated_at = datetime.now().isoformat()
            target.save()
            
            # 记录成功日志
            Log.create('success', 'env_manager', f'环境创建成功: {target.name}', user_id=user_id)
            
            return {
                'status': 'success',
                'target_id': target.target_id,
                'target_name': target.name,
                'containers': containers,
                'components': components
            }
            
        except Exception as e:
            logger.error(f"创建环境失败: {e}")
            Log.create('error', 'env_manager', f'环境创建失败: {str(e)}', user_id=user_id)
            return {
                'status': 'error',
                'msg': str(e)
            }
    
    def _parse_scenario(self, scenario_description):
        """解析场景描述，确定需要的组件"""
        # 使用AI模型解析场景描述（如果可用）
        try:
            from llm.local_model import LocalLLM
            llm = LocalLLM()
            
            prompt = f"""
            请分析以下靶场环境需求描述，并提取需要的组件：
            
            描述：{scenario_description}
            
            请返回一个JSON格式的组件列表，包含以下字段：
            - web_servers: Web服务器列表，每个包含type, version, vulnerable
            - databases: 数据库列表，每个包含type, version, vulnerable
            - network_devices: 网络设备列表，每个包含type, config
            - security_tools: 安全工具列表，每个包含type, config
            
            只返回JSON内容，不要其他文字。
            """
            
            result = llm.chat(prompt)
            import json
            ai_components = json.loads(result['content'].strip())
            return ai_components
            
        except Exception as e:
            # 如果AI解析失败，回退到关键词匹配
            logger.warning(f"AI解析场景失败，使用关键词匹配: {e}")
            components = {
                'web_servers': [],
                'databases': [],
                'network_devices': [],
                'security_tools': []
            }
            
            desc_lower = scenario_description.lower()
            
            if 'web' in desc_lower or 'website' in desc_lower or 'http' in desc_lower:
                components['web_servers'].append({
                    'type': 'nginx' if 'nginx' in desc_lower else 'apache',
                    'version': 'latest',
                    'vulnerable': True
                })
            
            if 'database' in desc_lower or 'mysql' in desc_lower or 'sql' in desc_lower:
                components['databases'].append({
                    'type': 'mysql' if 'mysql' in desc_lower else 'postgresql',
                    'version': '5.7' if 'mysql' in desc_lower else 'latest',
                    'vulnerable': True
                })
            
            if 'firewall' in desc_lower:
                components['network_devices'].append({
                    'type': 'iptables',
                    'config': 'default'
                })
            
            if 'waf' in desc_lower:
                components['security_tools'].append({
                    'type': 'modsecurity',
                    'config': 'owasp'
                })
            
            # 如果没有明确指定，添加一些常见的易受攻击的服务
            if not components['web_servers'] and not components['databases']:
                components['web_servers'].append({
                    'type': 'dvwa',
                    'version': 'latest',
                    'vulnerable': True
                })
            
            return components
    
    def _find_available_port(self):
        """查找可用端口"""
        import socket
        for port in range(8080, 9000):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                if result != 0:
                    return port
        return 8080  # 默认返回8080
    
    def _create_containers(self, components, target_id):
        """创建容器"""
        containers = []
        
        if not self.docker_client:
            raise Exception("Docker客户端未初始化")
        
        # 创建Web服务器容器
        for i, web_server in enumerate(components['web_servers']):
            container_name = f"web-{target_id}-{i}"
            try:
                if web_server['type'] == 'dvwa':
                    # 创建DVWA容器
                    container = self.docker_client.containers.run(
                        'vulnerables/web-dvwa:latest',
                        name=container_name,
                        ports={'80/tcp': self._find_available_port()},
                        detach=True,
                        environment={
                            'MYSQL_ROOT_PASSWORD': 'password',
                            'MYSQL_DATABASE': 'dvwa'
                        }
                    )
                elif web_server['type'] == 'nginx':
                    # 创建Nginx容器
                    container = self.docker_client.containers.run(
                        'nginx:latest',
                        name=container_name,
                        ports={'80/tcp': self._find_available_port()},
                        detach=True
                    )
                else:
                    # 默认Apache
                    container = self.docker_client.containers.run(
                        'httpd:2.4',
                        name=container_name,
                        ports={'80/tcp': self._find_available_port()},
                        detach=True
                    )
                
                containers.append({
                    'name': container_name,
                    'id': container.id,
                    'type': web_server['type'],
                    'status': 'running'
                })
                
            except Exception as e:
                logger.error(f"创建Web服务器容器失败: {e}")
                containers.append({
                    'name': container_name,
                    'type': web_server['type'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 创建数据库容器
        for i, database in enumerate(components['databases']):
            container_name = f"db-{target_id}-{i}"
            try:
                if database['type'] == 'mysql':
                    container = self.docker_client.containers.run(
                        'mysql:5.7',
                        name=container_name,
                        ports={'3306/tcp': self._find_available_port()},
                        environment={
                            'MYSQL_ROOT_PASSWORD': 'rootpassword',
                            'MYSQL_DATABASE': 'testdb'
                        },
                        detach=True
                    )
                else:
                    # PostgreSQL
                    container = self.docker_client.containers.run(
                        'postgres:13',
                        name=container_name,
                        ports={'5432/tcp': self._find_available_port()},
                        environment={
                            'POSTGRES_PASSWORD': 'password',
                            'POSTGRES_DB': 'testdb'
                        },
                        detach=True
                    )
                
                containers.append({
                    'name': container_name,
                    'id': container.id,
                    'type': database['type'],
                    'status': 'running'
                })
                
            except Exception as e:
                logger.error(f"创建数据库容器失败: {e}")
                containers.append({
                    'name': container_name,
                    'type': database['type'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return containers
    
    def destroy_environment(self, target_id, user_id=None):
        """销毁环境"""
        try:
            # 获取目标环境
            target = Target.get_by_id(target_id)
            if not target:
                return {'status': 'error', 'msg': '目标环境不存在'}
            
            # 停止并删除相关容器
            if target.config:
                config = json.loads(target.config)
                self._destroy_containers(config, target_id)
            
            # 删除目标记录
            target.delete()
            
            Log.create('info', 'env_manager', f'环境已销毁: {target.name}', user_id=user_id)
            
            return {'status': 'success', 'msg': '环境已销毁'}
            
        except Exception as e:
            logger.error(f"销毁环境失败: {e}")
            Log.create('error', 'env_manager', f'环境销毁失败: {str(e)}', user_id=user_id)
            return {'status': 'error', 'msg': str(e)}
    
    def _destroy_containers(self, config, target_id):
        """销毁容器"""
        if not self.docker_client:
            return
        
        # 停止Web服务器容器
        for i in range(len(config.get('web_servers', []))):
            container_name = f"web-{target_id}-{i}"
            try:
                container = self.docker_client.containers.get(container_name)
                container.stop()
                container.remove()
            except:
                pass  # 容器可能不存在
        
        # 停止数据库容器
        for i in range(len(config.get('databases', []))):
            container_name = f"db-{target_id}-{i}"
            try:
                container = self.docker_client.containers.get(container_name)
                container.stop()
                container.remove()
            except:
                pass  # 容器可能不存在
    
    def get_environment_status(self, target_id):
        """获取环境状态"""
        try:
            target = Target.get_by_id(target_id)
            if not target:
                return {'status': 'error', 'msg': '目标环境不存在'}
            
            # 检查相关容器状态
            if target.config:
                config = json.loads(target.config)
                containers_status = self._get_containers_status(config, target_id)
            else:
                containers_status = []
            
            return {
                'status': 'success',
                'target': target.to_dict(),
                'containers': containers_status
            }
            
        except Exception as e:
            logger.error(f"获取环境状态失败: {e}")
            return {'status': 'error', 'msg': str(e)}
    
    def _get_containers_status(self, config, target_id):
        """获取容器状态"""
        if not self.docker_client:
            return []
        
        containers_status = []
        
        # 检查Web服务器容器
        for i in range(len(config.get('web_servers', []))):
            container_name = f"web-{target_id}-{i}"
            try:
                container = self.docker_client.containers.get(container_name)
                containers_status.append({
                    'name': container_name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else 'unknown'
                })
            except:
                containers_status.append({
                    'name': container_name,
                    'status': 'not_found',
                    'image': 'unknown'
                })
        
        # 检查数据库容器
        for i in range(len(config.get('databases', []))):
            container_name = f"db-{target_id}-{i}"
            try:
                container = self.docker_client.containers.get(container_name)
                containers_status.append({
                    'name': container_name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else 'unknown'
                })
            except:
                containers_status.append({
                    'name': container_name,
                    'status': 'not_found',
                    'image': 'unknown'
                })
        
        return containers_status


# 全局实例
env_manager_agent = EnvManagerAgent()