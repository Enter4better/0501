# -*- coding: utf-8 -*-
"""
攻击路由 - 攻击管理API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import threading
import time
from datetime import datetime
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.attack import Attack
from models.defense import Defense
from models.log import Log
from services.database import db_service
from services.async_queue import async_queue_service
from config import ASYNC_CONFIG

attacks_bp = Blueprint('attacks', __name__, url_prefix='/api/attack')

# 攻击任务队列
attack_queue = []
attack_results = {}
attack_lock = threading.Lock()


def _trigger_defense_response(attack: Attack, user_id: str):
    """触发防御响应 - 攻防实时轮替"""
    try:
        # 获取所有启用的防御规则
        defenses = Defense.list_all(user_id)
        active_defenses = [d for d in defenses if d.enabled]
        
        defense_responses = []
        
        for defense in active_defenses:
            # 检查防御是否能拦截此攻击
            check_result = defense.check_attack(attack.attack_type, attack.intensity)
            
            if check_result['blocked']:
                defense_responses.append({
                    'defense_id': defense.defense_id,
                    'defense_name': defense.name,
                    'defense_type': defense.defense_type,
                    'blocked': True,
                    'message': check_result['message']
                })
                Log.create('success', 'defense', 
                          f'防御触发: {defense.name} 拦截了 {attack.attack_type} 攻击', 
                          user_id=user_id)
            else:
                defense_responses.append({
                    'defense_id': defense.defense_id,
                    'defense_name': defense.name,
                    'defense_type': defense.defense_type,
                    'blocked': False,
                    'message': check_result['message']
                })
        
        return defense_responses
    except Exception as e:
        current_app.logger.error(f"触发防御响应失败: {e}")
        return []


def _execute_attack_async(attack_id: str, attack: Attack):
    """异步执行攻击 - 攻防实时轮替"""
    try:
        # 更新攻击状态
        attack.update_status('running')
        
        # 记录攻击开始
        Log.create('info', 'attack', f'攻击发起: {attack.name} ({attack.attack_type})', 
                   user_id=attack.user_id, target_id=attack.target_id)
        
        # 实时触发防御响应 - 攻击发起后立即响应
        defense_responses = _trigger_defense_response(attack, attack.user_id)
        
        # 检查是否有防御成功拦截
        blocked_by = [d for d in defense_responses if d['blocked']]
        
        # 模拟攻击执行时间（根据强度调整）
        execution_time = random.uniform(0.5, 2.0) * (attack.intensity / 5)
        time.sleep(execution_time)
        
        # 执行攻击
        if blocked_by:
            # 被防御拦截
            result = {
                'success': False,
                'blocked': True,
                'blocked_by': blocked_by,
                'message': f'攻击被 {len(blocked_by)} 个防御规则拦截',
                'defense_responses': defense_responses
            }
            attack.update_status('blocked')
            Log.create('warning', 'attack', 
                      f'攻击被拦截: {attack.name} - 被 {blocked_by[0]["defense_name"]} 拦截', 
                      user_id=attack.user_id, target_id=attack.target_id)
        else:
            # 没有被拦截，执行攻击
            result = attack.execute()
            result['blocked'] = False
            result['defense_responses'] = defense_responses
            
            if result['success']:
                Log.create('success', 'attack', 
                          f'攻击成功: {attack.name} - {result["message"]}', 
                          user_id=attack.user_id, target_id=attack.target_id)
            else:
                Log.create('danger', 'attack', 
                          f'攻击失败: {attack.name} - {result["message"]}', 
                          user_id=attack.user_id, target_id=attack.target_id)
        
        # 保存结果
        with attack_lock:
            attack_results[attack_id] = result
        
    except Exception as e:
        # 记录错误
        Log.create('danger', 'attack', f'攻击执行异常: {attack.name} - {str(e)}', 
                   user_id=attack.user_id, target_id=attack.target_id)
        with attack_lock:
            attack_results[attack_id] = {'success': False, 'blocked': False, 'message': str(e)}


@attacks_bp.route('/types', methods=['GET'])
@jwt_required()
def get_attack_types():
    """获取攻击类型列表"""
    try:
        attack_types = Attack.get_attack_types()
        return jsonify({
            'status': 'success',
            'types': attack_types
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取攻击类型失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取攻击类型失败'}), 500


@attacks_bp.route('/list', methods=['GET'])
@jwt_required()
def list_attacks():
    """获取攻击记录列表"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        attacks = Attack.list_all(user_id, limit)
        
        # 获取攻击结果
        for attack in attacks:
            if attack.attack_id in attack_results:
                attack.result = attack_results[attack.attack_id]
        
        return jsonify({
            'status': 'success',
            'attacks': [attack.to_dict() for attack in attacks]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取攻击列表失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取攻击列表失败'}), 500


@attacks_bp.route('/create', methods=['POST'])
@jwt_required()
def create_attack():
    """创建新攻击"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'attack_type', 'target', 'port', 'intensity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'msg': f'{field} 是必填项'}), 400
        
        name = data['name']
        attack_type = data['attack_type']
        target = data['target']
        port = data['port']
        intensity = int(data['intensity'])
        
        # 验证强度值
        if intensity < 1 or intensity > 10:
            return jsonify({'status': 'error', 'msg': '攻击强度必须在1-10之间'}), 400
        
        # 创建攻击记录
        attack = Attack.create(name, attack_type, target, port, intensity, user_id)
        if not attack:
            return jsonify({'status': 'error', 'msg': '创建攻击失败'}), 500
        
        # 记录日志
        Log.create('info', 'attack', f'创建攻击任务: {name} ({attack_type})', 
                   user_id=user_id, target_id=attack.target_id)
        
        return jsonify({
            'status': 'success',
            'attack': attack.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"创建攻击失败: {e}")
        return jsonify({'status': 'error', 'msg': '创建攻击失败'}), 500


@attacks_bp.route('/execute/<attack_id>', methods=['POST'])
@jwt_required()
def execute_attack(attack_id):
    """执行攻击"""
    try:
        user_id = get_jwt_identity()
        attack = Attack.get_by_id(attack_id)
        
        if not attack:
            return jsonify({'status': 'error', 'msg': '攻击不存在'}), 404
        
        if attack.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        if attack.status != 'pending':
            return jsonify({'status': 'error', 'msg': '攻击任务状态不正确'}), 400
        
        # 添加到异步队列
        task_id = f"attack_{attack_id}_{int(time.time())}"
        async_queue_service.add_task(
            task_type='attack',
            func=_execute_attack_async,
            args=(attack_id, attack),
            priority=attack.intensity
        )
        
        # 记录日志
        Log.create('info', 'attack', f'攻击任务已加入队列: {attack.name}', 
                   user_id=user_id, target_id=attack.target_id)
        
        return jsonify({
            'status': 'success',
            'task_id': task_id,
            'message': '攻击任务已加入队列'
        }), 200
    except Exception as e:
        current_app.logger.error(f"执行攻击失败: {e}")
        return jsonify({'status': 'error', 'msg': '执行攻击失败'}), 500


@attacks_bp.route('/result/<attack_id>', methods=['GET'])
@jwt_required()
def get_attack_result(attack_id):
    """获取攻击结果"""
    try:
        user_id = get_jwt_identity()
        attack = Attack.get_by_id(attack_id)
        
        if not attack:
            return jsonify({'status': 'error', 'msg': '攻击不存在'}), 404
        
        if attack.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        # 获取攻击结果
        result = attack_results.get(attack_id)
        
        return jsonify({
            'status': 'success',
            'attack': attack.to_dict(),
            'result': result
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取攻击结果失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取攻击结果失败'}), 500


@attacks_bp.route('/batch-execute', methods=['POST'])
@jwt_required()
def batch_execute_attacks():
    """批量执行攻击"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('attack_ids'):
            return jsonify({'status': 'error', 'msg': '请选择要执行的攻击'}), 400
        
        attack_ids = data['attack_ids']
        tasks = []
        
        for attack_id in attack_ids:
            attack = Attack.get_by_id(attack_id)
            if not attack or attack.user_id != user_id:
                continue
            
            if attack.status == 'pending':
                task_id = f"attack_{attack_id}_{int(time.time())}"
                async_queue_service.add_task(
                    task_type='attack',
                    func=_execute_attack_async,
                    args=(attack_id, attack),
                    priority=attack.intensity
                )
                tasks.append(task_id)
        
        # 记录日志
        Log.create('info', 'attack', f'批量执行攻击任务: {len(tasks)} 个任务已加入队列', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'tasks': tasks,
            'message': f'成功添加 {len(tasks)} 个攻击任务到队列'
        }), 200
    except Exception as e:
        current_app.logger.error(f"批量执行攻击失败: {e}")
        return jsonify({'status': 'error', 'msg': '批量执行攻击失败'}), 500


@attacks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_attack_stats():
    """获取攻击统计信息"""
    try:
        user_id = get_jwt_identity()
        stats = Attack.get_stats()
        
        # 获取用户攻击统计
        user_attacks = Attack.list_all(user_id, 1000)
        user_stats = {
            'total': len(user_attacks),
            'success': len([a for a in user_attacks if a.status == 'completed']),
            'failed': len([a for a in user_attacks if a.status == 'failed']),
            'running': len([a for a in user_attacks if a.status == 'running'])
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'user_stats': user_stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取攻击统计失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取攻击统计失败'}), 500


@attacks_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_attack_templates():
    """获取攻击模板"""
    try:
        # 从数据库获取攻击模板
        conn = db_service.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, attack_type, description, config FROM defenses 
                WHERE defense_type IN ('WAF', 'IDS', 'IPS', '防火墙') 
                ORDER BY created_at DESC LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()
            
            # 如果没有从数据库获取到模板，则使用默认模板
            if not rows:
                templates = [
                    {
                        'name': 'Web应用渗透测试',
                        'attacks': [
                            {'name': 'SQL注入检测', 'type': 'SQL注入', 'target': '127.0.0.1', 'port': '80', 'intensity': 7},
                            {'name': 'XSS漏洞扫描', 'type': 'XSS攻击', 'target': '127.0.0.1', 'port': '80', 'intensity': 6},
                            {'name': '命令执行检测', 'type': '命令执行', 'target': '127.0.0.1', 'port': '80', 'intensity': 5}
                        ]
                    },
                    {
                        'name': '网络扫描',
                        'attacks': [
                            {'name': '端口扫描', 'type': '端口扫描', 'target': '127.0.0.1', 'port': '1-1000', 'intensity': 8},
                            {'name': '服务识别', 'type': '端口扫描', 'target': '127.0.0.1', 'port': '80,443,22', 'intensity': 6}
                        ]
                    },
                    {
                        'name': '暴力破解',
                        'attacks': [
                            {'name': 'SSH暴力破解', 'type': '暴力破解', 'target': '127.0.0.1', 'port': '22', 'intensity': 9},
                            {'name': 'FTP暴力破解', 'type': '暴力破解', 'target': '127.0.0.1', 'port': '21', 'intensity': 8}
                        ]
                    }
                ]
            else:
                # 根据防御规则生成攻击模板
                templates = []
                for row in rows[:3]:  # 取前3个防御规则作为模板基础
                    template = {
                        'name': f"{row['name']}反制方案",
                        'attacks': [
                            {
                                'name': f"{row['name']}绕过测试",
                                'type': 'SQL注入' if 'sql' in row['name'].lower() else '端口扫描',
                                'target': '127.0.0.1',
                                'port': '80',
                                'intensity': 7
                            }
                        ]
                    }
                    templates.append(template)
        else:
            # 数据库连接失败时使用默认模板
            templates = [
                {
                    'name': 'Web应用渗透测试',
                    'attacks': [
                        {'name': 'SQL注入检测', 'type': 'SQL注入', 'target': '127.0.0.1', 'port': '80', 'intensity': 7},
                        {'name': 'XSS漏洞扫描', 'type': 'XSS攻击', 'target': '127.0.0.1', 'port': '80', 'intensity': 6},
                        {'name': '命令执行检测', 'type': '命令执行', 'target': '127.0.0.1', 'port': '80', 'intensity': 5}
                    ]
                },
                {
                    'name': '网络扫描',
                    'attacks': [
                        {'name': '端口扫描', 'type': '端口扫描', 'target': '127.0.0.1', 'port': '1-1000', 'intensity': 8},
                        {'name': '服务识别', 'type': '端口扫描', 'target': '127.0.0.1', 'port': '80,443,22', 'intensity': 6}
                    ]
                },
                {
                    'name': '暴力破解',
                    'attacks': [
                        {'name': 'SSH暴力破解', 'type': '暴力破解', 'target': '127.0.0.1', 'port': '22', 'intensity': 9},
                        {'name': 'FTP暴力破解', 'type': '暴力破解', 'target': '127.0.0.1', 'port': '21', 'intensity': 8}
                    ]
                }
            ]
        
        return jsonify({
            'status': 'success',
            'templates': templates
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取攻击模板失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取攻击模板失败'}), 500


@attacks_bp.route('/template/execute/<template_name>', methods=['POST'])
@jwt_required()
def execute_attack_template(template_name):
    """执行攻击模板"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 获取模板
        templates = {
            'Web应用渗透测试': [
                {'name': 'SQL注入检测', 'type': 'SQL注入', 'target': data.get('target', '127.0.0.1'), 'port': '80', 'intensity': 7},
                {'name': 'XSS漏洞扫描', 'type': 'XSS攻击', 'target': data.get('target', '127.0.0.1'), 'port': '80', 'intensity': 6},
                {'name': '命令执行检测', 'type': '命令执行', 'target': data.get('target', '127.0.0.1'), 'port': '80', 'intensity': 5}
            ],
            '网络扫描': [
                {'name': '端口扫描', 'type': '端口扫描', 'target': data.get('target', '127.0.0.1'), 'port': '1-1000', 'intensity': 8},
                {'name': '服务识别', 'type': '端口扫描', 'target': data.get('target', '127.0.0.1'), 'port': '80,443,22', 'intensity': 6}
            ],
            '暴力破解': [
                {'name': 'SSH暴力破解', 'type': '暴力破解', 'target': data.get('target', '127.0.0.1'), 'port': '22', 'intensity': 9},
                {'name': 'FTP暴力破解', 'type': '暴力破解', 'target': data.get('target', '127.0.0.1'), 'port': '21', 'intensity': 8}
            ]
        }
        
        if template_name not in templates:
            return jsonify({'status': 'error', 'msg': '模板不存在'}), 404
        
        attacks = templates[template_name]
        created_attacks = []
        
        # 创建攻击任务
        for attack_data in attacks:
            attack = Attack.create(
                attack_data['name'],
                attack_data['type'],
                attack_data['target'],
                attack_data['port'],
                attack_data['intensity'],
                user_id
            )
            if attack:
                created_attacks.append(attack)
        
        # 批量执行攻击
        tasks = []
        for attack in created_attacks:
            task_id = f"attack_{attack.attack_id}_{int(time.time())}"
            async_queue_service.add_task(
                task_type='attack',
                func=_execute_attack_async,
                args=(attack.attack_id, attack),
                priority=attack.intensity
            )
            tasks.append(task_id)
        
        # 记录日志
        Log.create('info', 'attack', f'执行攻击模板: {template_name} - {len(tasks)} 个任务已加入队列', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'template': template_name,
            'created_attacks': len(created_attacks),
            'tasks': tasks,
            'message': f'成功创建 {len(created_attacks)} 个攻击任务，{len(tasks)} 个任务已加入队列'
        }), 200
    except Exception as e:
        current_app.logger.error(f"执行攻击模板失败: {e}")
        return jsonify({'status': 'error', 'msg': '执行攻击模板失败'}), 500