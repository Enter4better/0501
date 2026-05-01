# -*- coding: utf-8 -*-
"""
防御路由 - 防御管理API
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

from models.defense import Defense
from models.attack import Attack
from models.log import Log
from services.database import db_service
from services.async_queue import async_queue_service
from config import ASYNC_CONFIG

defenses_bp = Blueprint('defenses', __name__, url_prefix='/api/defense')
defenses_alt_bp = Blueprint('defenses_alt', __name__, url_prefix='/api/defenses')

# 防御任务队列
defense_queue = []
defense_results = {}
defense_lock = threading.Lock()


def _check_defense_async(defense_id: str, defense: Defense, attack_data: dict):
    """异步检查防御"""
    try:
        # 更新防御状态
        defense.update_status('running')
        
        # 记录防御检查开始
        Log.create('info', 'defense', f'开始检查防御: {defense.name}', 
                   user_id=defense.user_id)
        
        # 模拟检查时间
        time.sleep(random.uniform(0.5, 1.5))
        
        # 检查攻击
        result = defense.check_attack(attack_data['attack_type'], attack_data['intensity'])
        
        # 保存结果
        with defense_lock:
            defense_results[defense_id] = result
        
        # 记录防御结果
        if result['blocked']:
            Log.create('success', 'defense', 
                      f'防御成功: {defense.name} 拦截了 {attack_data["attack_type"]}', 
                      user_id=defense.user_id)
        else:
            Log.create('danger', 'defense', 
                      f'防御失败: {defense.name} 未能拦截 {attack_data["attack_type"]}', 
                      user_id=defense.user_id)
        
    except Exception as e:
        # 记录错误
        Log.create('danger', 'defense', f'防御检查异常: {defense.name} - {str(e)}', 
                   user_id=defense.user_id)
        with defense_lock:
            defense_results[defense_id] = {'blocked': False, 'message': str(e)}


@defenses_bp.route('/list', methods=['GET'])
@jwt_required()
def list_defenses():
    """获取防御规则列表"""
    try:
        user_id = get_jwt_identity()
        
        defenses = Defense.list_all(user_id)
        
        return jsonify({
            'status': 'success',
            'defenses': [defense.to_dict() for defense in defenses],
            'data': [defense.to_dict() for defense in defenses]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御列表失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御列表失败'}), 500


@defenses_bp.route('', methods=['GET'])
@jwt_required()
def list_defenses_alt():
    """获取防御规则列表（备用路由）"""
    return list_defenses()


@defenses_bp.route('/create', methods=['POST'])
@jwt_required()
def create_defense():
    """创建新防御规则"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'defense_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'msg': f'{field} 是必填项'}), 400
        
        name = data['name']
        defense_type = data['defense_type']
        description = data.get('description', '')
        enabled = data.get('enabled', True)
        coverage = float(data.get('coverage', 0.0))
        
        # 验证覆盖率
        if coverage < 0 or coverage > 100:
            return jsonify({'status': 'error', 'msg': '覆盖率必须在0-100之间'}), 400
        
        # 创建防御规则
        defense = Defense.create(name, defense_type, description, enabled, coverage, user_id)
        if not defense:
            return jsonify({'status': 'error', 'msg': '创建防御规则失败'}), 500
        
        # 记录日志
        Log.create('success', 'defense', f'创建防御规则: {name}', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'defense': defense.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"创建防御规则失败: {e}")
        return jsonify({'status': 'error', 'msg': '创建防御规则失败'}), 500


@defenses_bp.route('/update/<defense_id>', methods=['PUT'])
@jwt_required()
def update_defense(defense_id):
    """更新防御规则"""
    try:
        user_id = get_jwt_identity()
        defense = Defense.get_by_id(defense_id)
        
        if not defense:
            return jsonify({'status': 'error', 'msg': '防御规则不存在'}), 404
        
        if defense.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        data = request.get_json()
        
        # 更新防御规则
        success = defense.update(
            name=data.get('name'),
            defense_type=data.get('defense_type'),
            description=data.get('description'),
            enabled=data.get('enabled'),
            coverage=data.get('coverage')
        )
        
        if not success:
            return jsonify({'status': 'error', 'msg': '更新防御规则失败'}), 500
        
        # 记录日志
        Log.create('info', 'defense', f'更新防御规则: {defense.name}', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'defense': defense.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"更新防御规则失败: {e}")
        return jsonify({'status': 'error', 'msg': '更新防御规则失败'}), 500


@defenses_bp.route('/toggle/<defense_id>', methods=['POST'])
@jwt_required()
def toggle_defense(defense_id):
    """切换防御规则状态"""
    try:
        user_id = get_jwt_identity()
        defense = Defense.get_by_id(defense_id)
        
        if not defense:
            return jsonify({'status': 'error', 'msg': '防御规则不存在'}), 404
        
        if defense.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        # 切换状态
        success = defense.toggle()
        
        if not success:
            return jsonify({'status': 'error', 'msg': '切换防御规则状态失败'}), 500
        
        # 记录日志
        status = '启用' if defense.enabled else '禁用'
        Log.create('info', 'defense', f'{status}防御规则: {defense.name}', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'defense': defense.to_dict(),
            'message': f'防御规则已{status}'
        }), 200
    except Exception as e:
        current_app.logger.error(f"切换防御规则状态失败: {e}")
        return jsonify({'status': 'error', 'msg': '切换防御规则状态失败'}), 500


@defenses_bp.route('/delete/<defense_id>', methods=['DELETE'])
@jwt_required()
def delete_defense(defense_id):
    """删除防御规则"""
    try:
        user_id = get_jwt_identity()
        defense = Defense.get_by_id(defense_id)
        
        if not defense:
            return jsonify({'status': 'error', 'msg': '防御规则不存在'}), 404
        
        if defense.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        # 删除防御规则
        success = defense.delete()
        
        if not success:
            return jsonify({'status': 'error', 'msg': '删除防御规则失败'}), 500
        
        # 记录日志
        Log.create('info', 'defense', f'删除防御规则: {defense.name}', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'message': '防御规则已删除'
        }), 200
    except Exception as e:
        current_app.logger.error(f"删除防御规则失败: {e}")
        return jsonify({'status': 'error', 'msg': '删除防御规则失败'}), 500


@defenses_bp.route('/check', methods=['POST'])
@jwt_required()
def check_defense():
    """检查防御规则"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['defense_id', 'attack_type', 'intensity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'msg': f'{field} 是必填项'}), 400
        
        defense_id = data['defense_id']
        attack_type = data['attack_type']
        intensity = int(data['intensity'])
        
        # 验证强度值
        if intensity < 1 or intensity > 10:
            return jsonify({'status': 'error', 'msg': '攻击强度必须在1-10之间'}), 400
        
        # 获取防御规则
        defense = Defense.get_by_id(defense_id)
        
        if not defense:
            return jsonify({'status': 'error', 'msg': '防御规则不存在'}), 404
        
        if defense.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        # 添加到异步队列
        task_id = f"defense_{defense_id}_{int(time.time())}"
        async_queue_service.add_task(
            task_type='defense',
            func=_check_defense_async,
            args=(defense_id, defense, {
                'attack_type': attack_type,
                'intensity': intensity
            }),
            priority=5
        )
        
        # 记录日志
        Log.create('info', 'defense', f'防御检查任务已加入队列: {defense.name}', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'task_id': task_id,
            'message': '防御检查任务已加入队列'
        }), 200
    except Exception as e:
        current_app.logger.error(f"检查防御规则失败: {e}")
        return jsonify({'status': 'error', 'msg': '检查防御规则失败'}), 500


@defenses_bp.route('/result/<defense_id>', methods=['GET'])
@jwt_required()
def get_defense_result(defense_id):
    """获取防御检查结果"""
    try:
        user_id = get_jwt_identity()
        defense = Defense.get_by_id(defense_id)
        
        if not defense:
            return jsonify({'status': 'error', 'msg': '防御规则不存在'}), 404
        
        if defense.user_id != user_id:
            return jsonify({'status': 'error', 'msg': '权限不足'}), 403
        
        # 获取防御结果
        result = defense_results.get(defense_id)
        
        return jsonify({
            'status': 'success',
            'defense': defense.to_dict(),
            'result': result
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御结果失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御结果失败'}), 500


@defenses_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_defense_stats():
    """获取防御统计信息"""
    try:
        user_id = get_jwt_identity()
        stats = Defense.get_stats()
        
        # 获取用户防御统计
        user_defenses = Defense.list_all(user_id)
        enabled_defenses = [d for d in user_defenses if d.enabled]
        user_stats = {
            'total': len(user_defenses),
            'enabled': len(enabled_defenses),
            'disabled': len(user_defenses) - len(enabled_defenses),
            'avg_coverage': sum(d.coverage for d in enabled_defenses) / len(enabled_defenses) if enabled_defenses else 0
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'user_stats': user_stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御统计失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御统计失败'}), 500


@defenses_bp.route('/types', methods=['GET'])
@jwt_required()
def get_defense_types():
    """获取防御类型列表"""
    try:
        defense_types = Defense.get_defense_types()
        return jsonify({
            'status': 'success',
            'types': defense_types
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御类型失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御类型失败'}), 500


@defenses_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_defense_templates():
    """获取防御模板"""
    try:
        # 从数据库获取防御模板
        conn = db_service.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, defense_type, description, coverage, config FROM defenses 
                WHERE enabled = 1 
                ORDER BY created_at DESC LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()
            
            # 如果没有从数据库获取到模板，则使用默认模板
            if not rows:
                templates = [
                    {
                        'name': 'Web应用安全防护',
                        'defenses': [
                            {'name': 'SQL注入防护', 'type': 'WAF', 'description': '检测并阻止SQL注入攻击', 'coverage': 92.0},
                            {'name': 'XSS攻击拦截', 'type': 'WAF', 'description': '检测并阻止跨站脚本攻击', 'coverage': 88.0},
                            {'name': 'CSRF防护', 'type': 'WAF', 'description': '防止跨站请求伪造', 'coverage': 85.0}
                        ]
                    },
                    {
                        'name': '网络安全防护',
                        'defenses': [
                            {'name': '端口扫描检测', 'type': 'IDS', 'description': '检测端口扫描行为', 'coverage': 95.0},
                            {'name': '暴力破解阻断', 'type': 'IPS', 'description': '阻止暴力破解攻击', 'coverage': 78.0},
                            {'name': '防火墙规则', 'type': '防火墙', 'description': '控制网络流量', 'coverage': 90.0}
                        ]
                    },
                    {
                        'name': '蜜罐诱捕系统',
                        'defenses': [
                            {'name': '蜜罐诱饵节点', 'type': '蜜罐', 'description': '诱捕攻击者', 'coverage': 0.0},
                            {'name': '入侵检测', 'type': '入侵检测', 'description': '实时监控威胁', 'coverage': 82.0}
                        ]
                    }
                ]
            else:
                # 根据现有防御规则生成模板
                templates = []
                for row in rows[:3]:  # 取前3个防御规则作为模板基础
                    template = {
                        'name': f"{row['name']}增强版",
                        'defenses': [
                            {
                                'name': f"{row['name']}增强配置",
                                'type': row['defense_type'],
                                'description': row['description'],
                                'coverage': row['coverage']
                            }
                        ]
                    }
                    templates.append(template)
        else:
            # 数据库连接失败时使用默认模板
            templates = [
                {
                    'name': 'Web应用安全防护',
                    'defenses': [
                        {'name': 'SQL注入防护', 'type': 'WAF', 'description': '检测并阻止SQL注入攻击', 'coverage': 92.0},
                        {'name': 'XSS攻击拦截', 'type': 'WAF', 'description': '检测并阻止跨站脚本攻击', 'coverage': 88.0},
                        {'name': 'CSRF防护', 'type': 'WAF', 'description': '防止跨站请求伪造', 'coverage': 85.0}
                    ]
                },
                {
                    'name': '网络安全防护',
                    'defenses': [
                        {'name': '端口扫描检测', 'type': 'IDS', 'description': '检测端口扫描行为', 'coverage': 95.0},
                        {'name': '暴力破解阻断', 'type': 'IPS', 'description': '阻止暴力破解攻击', 'coverage': 78.0},
                        {'name': '防火墙规则', 'type': '防火墙', 'description': '控制网络流量', 'coverage': 90.0}
                    ]
                },
                {
                    'name': '蜜罐诱捕系统',
                    'defenses': [
                        {'name': '蜜罐诱饵节点', 'type': '蜜罐', 'description': '诱捕攻击者', 'coverage': 0.0},
                        {'name': '入侵检测', 'type': '入侵检测', 'description': '实时监控威胁', 'coverage': 82.0}
                    ]
                }
            ]
        
        return jsonify({
            'status': 'success',
            'templates': templates
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御模板失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御模板失败'}), 500


@defenses_bp.route('/template/apply/<template_name>', methods=['POST'])
@jwt_required()
def apply_defense_template(template_name):
    """应用防御模板"""
    try:
        user_id = get_jwt_identity()
        
        # 获取模板
        templates = {
            'Web应用安全防护': [
                {'name': 'SQL注入防护', 'type': 'WAF', 'description': '检测并阻止SQL注入攻击', 'coverage': 92.0},
                {'name': 'XSS攻击拦截', 'type': 'WAF', 'description': '检测并阻止跨站脚本攻击', 'coverage': 88.0},
                {'name': 'CSRF防护', 'type': 'WAF', 'description': '防止跨站请求伪造', 'coverage': 85.0}
            ],
            '网络安全防护': [
                {'name': '端口扫描检测', 'type': 'IDS', 'description': '检测端口扫描行为', 'coverage': 95.0},
                {'name': '暴力破解阻断', 'type': 'IPS', 'description': '阻止暴力破解攻击', 'coverage': 78.0},
                {'name': '防火墙规则', 'type': '防火墙', 'description': '控制网络流量', 'coverage': 90.0}
            ],
            '蜜罐诱捕系统': [
                {'name': '蜜罐诱饵节点', 'type': '蜜罐', 'description': '诱捕攻击者', 'coverage': 0.0},
                {'name': '入侵检测', 'type': '入侵检测', 'description': '实时监控威胁', 'coverage': 82.0}
            ]
        }
        
        if template_name not in templates:
            return jsonify({'status': 'error', 'msg': '模板不存在'}), 404
        
        defenses = templates[template_name]
        created_defenses = []
        
        # 创建防御规则
        for defense_data in defenses:
            defense = Defense.create(
                defense_data['name'],
                defense_data['type'],
                defense_data['description'],
                True,  # 默认启用
                defense_data['coverage'],
                user_id
            )
            if defense:
                created_defenses.append(defense)
        
        # 记录日志
        Log.create('success', 'defense', f'应用防御模板: {template_name} - 创建了 {len(created_defenses)} 个防御规则', 
                   user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'template': template_name,
            'created_defenses': len(created_defenses),
            'message': f'成功应用 {template_name} 模板，创建了 {len(created_defenses)} 个防御规则'
        }), 200
    except Exception as e:
        current_app.logger.error(f"应用防御模板失败: {e}")
        return jsonify({'status': 'error', 'msg': '应用防御模板失败'}), 500


# 兼容前端API的路由（/api/defenses前缀）
@defenses_alt_bp.route('', methods=['GET'])
@jwt_required()
def alt_list_defenses():
    """获取防御规则列表 - 兼容前端"""
    try:
        user_id = get_jwt_identity()
        
        defenses = Defense.list_all(user_id)
        
        return jsonify({
            'status': 'success',
            'data': [defense.to_dict() for defense in defenses]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御列表失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御列表失败'}), 500


@defenses_alt_bp.route('/create', methods=['POST'])
@jwt_required()
def alt_create_defense():
    """创建防御规则 - 兼容前端"""
    return create_defense()


@defenses_alt_bp.route('/<defense_id>/toggle', methods=['POST'])
@jwt_required()
def alt_toggle_defense(defense_id):
    """切换防御规则状态 - 兼容前端"""
    return toggle_defense(defense_id)


@defenses_alt_bp.route('/<defense_id>/update', methods=['PUT'])
@jwt_required()
def alt_update_defense(defense_id):
    """更新防御规则 - 兼容前端"""
    return update_defense(defense_id)


@defenses_alt_bp.route('/<defense_id>/delete', methods=['DELETE'])
@jwt_required()
def alt_delete_defense(defense_id):
    """删除防御规则 - 兼容前端"""
    return delete_defense(defense_id)


@defenses_alt_bp.route('/check', methods=['POST'])
@jwt_required()
def alt_check_defense():
    """检查防御 - 兼容前端"""
    return check_defense()


@defenses_alt_bp.route('/result/<defense_id>', methods=['GET'])
@jwt_required()
def alt_defense_result(defense_id):
    """获取防御结果 - 兼容前端"""
    return get_defense_result(defense_id)


@defenses_alt_bp.route('/template/apply/<template_name>', methods=['POST'])
@jwt_required()
def alt_apply_template(template_name):
    """应用模板 - 兼容前端"""
    return apply_defense_template(template_name)
