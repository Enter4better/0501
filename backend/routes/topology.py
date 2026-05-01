# -*- coding: utf-8 -*-
"""
拓扑路由 - 网络拓扑管理API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.target import Target
from models.log import Log
from services.database import db_service

topology_bp = Blueprint('topology', __name__, url_prefix='/api/topology')


@topology_bp.route('/', methods=['GET'])
def get_topology():
    """获取网络拓扑数据（无需认证）"""
    try:
        # 获取所有目标环境
        targets = Target.list_all()
        
        # 构建拓扑数据
        nodes = []
        edges = []
        
        # 添加中心节点（靶场服务器）
        nodes.append({
            'id': 'server',
            'label': '靶场服务器',
            'type': 'server',
            'status': 'online',
            'ip': '127.0.0.1'
        })
        
        # 添加目标节点
        if targets:
            for target in targets:
                node = {
                    'id': str(target.target_id),
                    'label': target.name,
                    'type': target.type or 'target',
                    'status': target.status or 'offline',
                    'ip': target.ip or 'unknown'
                }
                nodes.append(node)
                
                # 添加连接边
                edges.append({
                    'source': 'server',
                    'target': str(target.target_id),
                    'type': 'network'
                })
        
        return jsonify({
            'status': 'success',
            'nodes': nodes,
            'edges': edges,
            'total': len(nodes)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取拓扑数据失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '获取拓扑数据失败'
        }), 500


@topology_bp.route('/list', methods=['GET'])
@jwt_required()
def list_topology():
    """获取网络拓扑列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取所有目标环境
        targets = Target.list_all()
        
        # 构建拓扑数据
        nodes = []
        edges = []
        
        # 添加中心节点（靶场服务器）
        nodes.append({
            'id': 'server',
            'label': '靶场服务器',
            'type': 'server',
            'status': 'online',
            'ip': '127.0.0.1'
        })
        
        # 添加目标节点
        if targets:
            for target in targets:
                node = {
                    'id': str(target.target_id),
                    'label': target.name,
                    'type': target.type or 'target',
                    'status': target.status or 'offline',
                    'ip': target.ip or 'unknown'
                }
                nodes.append(node)
                
                # 添加连接边
                edges.append({
                    'source': 'server',
                    'target': str(target.target_id),
                    'type': 'network'
                })
        
        return jsonify({
            'status': 'success',
            'nodes': nodes,
            'edges': edges,
            'total': len(nodes)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取拓扑列表失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '获取拓扑列表失败，请检查数据库连接'
        }), 500


@topology_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan_topology():
    """扫描网络拓扑"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        target_ip = data.get('ip', '192.168.1.0/24')
        scan_type = data.get('scan_type', 'quick')
        
        # 记录日志
        Log.create('info', 'topology', f'开始扫描网络拓扑: {target_ip}', user_id=user_id)
        
        # 扫描功能尚未实现
        return jsonify({
            'status': 'error',
            'msg': '网络扫描功能尚未实现，需要配置相应的扫描工具'
        }), 500
        
    except Exception as e:
        current_app.logger.error(f"扫描拓扑失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '扫描拓扑失败'
        }), 500


@topology_bp.route('/node/<node_id>', methods=['GET'])
@jwt_required()
def get_node(node_id):
    """获取节点详情"""
    try:
        user_id = get_jwt_identity()
        
        if node_id == 'server':
            return jsonify({
                'status': 'success',
                'node': {
                    'id': 'server',
                    'label': '靶场服务器',
                    'type': 'server',
                    'status': 'online',
                    'ip': '127.0.0.1'
                }
            }), 200
        
        # 从数据库获取目标节点
        target = Target.get_by_id(int(node_id))
        if target:
            return jsonify({
                'status': 'success',
                'node': {
                    'id': str(target.target_id),
                    'label': target.name,
                    'type': target.type or 'target',
                    'status': target.status or 'offline',
                    'ip': target.ip or 'unknown',
                    'os': target.os or 'unknown',
                    'ports': target.ports or [],
                    'services': target.services or []
                }
            }), 200
        
        return jsonify({
            'status': 'error',
            'msg': '节点不存在'
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"获取节点详情失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '获取节点详情失败'
        }), 500


@topology_bp.route('/node/<node_id>/status', methods=['PUT'])
@jwt_required()
def update_node_status(node_id):
    """更新节点状态"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        status = data.get('status', 'offline')
        
        # 更新数据库
        if node_id != 'server':
            target = Target.get_by_id(int(node_id))
            if target:
                target.update_status(status)
                Log.create('info', 'topology', f'节点{node_id}状态更新为{status}', user_id=user_id)
                
                return jsonify({
                    'status': 'success',
                    'msg': '节点状态已更新',
                    'node_id': node_id,
                    'new_status': status
                }), 200
        
        return jsonify({
            'status': 'error',
            'msg': '节点不存在'
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"更新节点状态失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '更新节点状态失败'
        }), 500


@topology_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_topology():
    """刷新拓扑数据"""
    try:
        user_id = get_jwt_identity()
        
        # 重新获取所有目标
        targets = Target.list_all()
        
        nodes = []
        edges = []
        
        # 添加中心节点
        nodes.append({
            'id': 'server',
            'label': '靶场服务器',
            'type': 'server',
            'status': 'online',
            'ip': '127.0.0.1'
        })
        
        # 添加目标节点
        if targets:
            for target in targets:
                nodes.append({
                    'id': str(target.target_id),
                    'label': target.name,
                    'type': target.type or 'target',
                    'status': target.status or 'offline',
                    'ip': target.ip or 'unknown'
                })
                
                edges.append({
                    'source': 'server',
                    'target': str(target.target_id),
                    'type': 'network'
                })
        
        Log.create('success', 'topology', '拓扑数据已刷新', user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'msg': '拓扑数据已刷新',
            'nodes': nodes,
            'edges': edges,
            'total': len(nodes)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"刷新拓扑失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '刷新拓扑失败'
        }), 500


@topology_bp.route('/export', methods=['GET'])
@jwt_required()
def export_topology():
    """导出拓扑数据"""
    try:
        user_id = get_jwt_identity()
        
        # 获取拓扑数据
        targets = Target.list_all()
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'nodes': [],
            'edges': []
        }
        
        # 添加中心节点
        export_data['nodes'].append({
            'id': 'server',
            'label': '靶场服务器',
            'type': 'server',
            'ip': '127.0.0.1'
        })
        
        # 添加目标节点
        if targets:
            for target in targets:
                export_data['nodes'].append({
                    'id': str(target.target_id),
                    'label': target.name,
                    'type': target.type or 'target',
                    'ip': target.ip or 'unknown'
                })
                
                export_data['edges'].append({
                    'source': 'server',
                    'target': str(target.target_id)
                })
        
        return jsonify({
            'status': 'success',
            'data': export_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"导出拓扑失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '导出拓扑失败'
        }), 500