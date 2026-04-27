from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import random
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

topology_bp = Blueprint('topology', __name__, url_prefix='/api/topology')

# 默认拓扑数据
DEFAULT_TOPOLOGY = {
    'nodes': [
        {'id': 'router1', 'name': 'Router', 'type': 'router', 'x': 50, 'y': 10, 'status': 'running'},
        {'id': 'fw1', 'name': 'Firewall', 'type': 'firewall', 'x': 50, 'y': 25, 'status': 'running'},
        {'id': 'ids1', 'name': 'IDS', 'type': 'ids', 'x': 30, 'y': 35, 'status': 'running'},
        {'id': 'switch1', 'name': 'Switch', 'type': 'switch', 'x': 50, 'y': 40, 'status': 'running'},
        {'id': 'attacker1', 'name': 'Attacker', 'type': 'attacker', 'x': 15, 'y': 55, 'status': 'running'},
        {'id': 'target1', 'name': 'Target-1', 'type': 'target', 'x': 40, 'y': 60, 'status': 'running'},
        {'id': 'target2', 'name': 'Target-2', 'type': 'target', 'x': 60, 'y': 60, 'status': 'running'},
        {'id': 'dmz1', 'name': 'DMZ', 'type': 'dmz', 'x': 75, 'y': 45, 'status': 'running'},
        {'id': 'log1', 'name': 'LogServer', 'type': 'logserver', 'x': 85, 'y': 25, 'status': 'running'}
    ],
    'links': [
        {'source': 'router1', 'target': 'fw1', 'active': True},
        {'source': 'fw1', 'target': 'switch1', 'active': True},
        {'source': 'fw1', 'target': 'ids1', 'active': True},
        {'source': 'switch1', 'target': 'target1', 'active': True},
        {'source': 'switch1', 'target': 'target2', 'active': True},
        {'source': 'switch1', 'target': 'dmz1', 'active': False},
        {'source': 'attacker1', 'target': 'ids1', 'active': True},
        {'source': 'ids1', 'target': 'log1', 'active': True},
        {'source': 'dmz1', 'target': 'log1', 'active': False}
    ]
}

@topology_bp.route('/', methods=['GET'])
def get_topology():
    """获取网络拓扑数据"""
    try:
        return jsonify({
            'status': 'success',
            'nodes': DEFAULT_TOPOLOGY['nodes'],
            'links': DEFAULT_TOPOLOGY['links'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取拓扑数据失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '获取拓扑数据失败'
        }), 500

@topology_bp.route('/ping', methods=['POST'])
@jwt_required()
def ping_node():
    """Ping测试节点"""
    try:
        data = request.get_json()
        node_id = data.get('node_id')
        
        if not node_id:
            return jsonify({
                'status': 'error',
                'msg': '节点ID不能为空'
            }), 400
        
        # 模拟Ping结果
        latency = random.randint(5, 25)
        result = f"""PING {node_id}:
64 bytes from {node_id}: seq=1 ttl=64 time={latency}ms
64 bytes from {node_id}: seq=2 ttl=64 time={latency+2}ms
64 bytes from {node_id}: seq=3 ttl=64 time={latency-1}ms

--- {node_id} ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
round-trip min/avg/max = {latency-1}/{latency+0.33}/{latency+2} ms"""
        
        return jsonify({
            'status': 'success',
            'result': result,
            'latency': latency,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Ping测试失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': 'Ping测试失败'
        }), 500

@topology_bp.route('/ssh', methods=['POST'])
@jwt_required()
def ssh_node():
    """SSH连接节点"""
    try:
        data = request.get_json()
        node_id = data.get('node_id')
        
        if not node_id:
            return jsonify({
                'status': 'error',
                'msg': '节点ID不能为空'
            }), 400
        
        # 模拟SSH连接结果
        result = f"""Connecting to {node_id}...
SSH connection established.
Terminal ready: /dev/tty1
Host: {node_id}
User: admin
Last login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        return jsonify({
            'status': 'success',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"SSH连接失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': 'SSH连接失败'
        }), 500

@topology_bp.route('/restart', methods=['POST'])
@jwt_required()
def restart_node():
    """重启节点"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        node_id = data.get('node_id')
        
        if not node_id:
            return jsonify({
                'status': 'error',
                'msg': '节点ID不能为空'
            }), 400
        
        # 模拟重启结果
        result = f"""Stopping {node_id}...
Services stopped.
Starting {node_id}...
Services started.
Status: running
Uptime: 0s"""
        
        from models.log import Log
        Log.create('warning', 'topology', f'节点重启: {node_id}', user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"节点重启失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '节点重启失败'
        }), 500

@topology_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan_network():
    """扫描网络"""
    try:
        user_id = get_jwt_identity()
        
        # 模拟扫描结果
        scanned_nodes = DEFAULT_TOPOLOGY['nodes']
        
        from models.log import Log
        Log.create('info', 'topology', '网络扫描完成', user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'nodes': scanned_nodes,
            'links': DEFAULT_TOPOLOGY['links'],
            'msg': '扫描完成，发现{}个节�?.format(len(scanned_nodes)),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"网络扫描失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '网络扫描失败'
        }), 500

@topology_bp.route('/connectivity', methods=['GET'])
@jwt_required()
def check_connectivity():
    """检查网络连通�?""
    try:
        # 模拟连通性测试结�?
        bandwidth = round(random.uniform(0.8, 1.5), 2)
        latency = random.randint(8, 20)
        packet_loss = round(random.uniform(0, 0.05), 2)
        
        return jsonify({
            'status': 'success',
            'bandwidth': str(bandwidth),
            'latency': str(latency),
            'packet_loss': str(packet_loss),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"连通性测试失�? {e}")
        return jsonify({
            'status': 'error',
            'msg': '连通性测试失�?
        }), 500

@topology_bp.route('/flow', methods=['GET'])
def get_flow_data():
    """获取流量数据"""
    try:
        # 模拟流量数据
        flow_data = []
        for i in range(10):
            flow_data.append({
                'time': datetime.now().isoformat(),
                'in': random.randint(100, 500),
                'out': random.randint(50, 300)
            })
        
        return jsonify({
            'status': 'success',
            'flow': flow_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取流量数据失败: {e}")
        return jsonify({
            'status': 'error',
            'msg': '获取流量数据失败'
        }), 500
