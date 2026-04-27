"""
AI攻防靶场管理系统 - 后端启动入口
直接运行此文件启动后端服务
"""
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cyber-range-secret-key-2024')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'msg': '令牌已过期，请重新登录'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'status': 'error',
            'msg': '无效的令牌'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'status': 'error',
            'msg': '缺少认证令牌'
        }), 401
    
    # ==================== 健康检查 ====================
    @app.route('/api/health')
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'ok',
            'database': 'demo_mode',
            'timestamp': datetime.now().isoformat()
        })
    
    # ==================== 系统信息 ====================
    @app.route('/api/system/info')
    def system_info():
        """获取系统信息"""
        return jsonify({
            'name': 'AI攻防靶场管理系统',
            'version': '1.0.0',
            'mode': 'demo',
            'timestamp': datetime.now().isoformat()
        })
    
    # ==================== 认证接口 ====================
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        data = request.get_json() or {}
        username = data.get('username', '')
        password = data.get('password', '')
        
        # 演示模式：允许任意登录
        if username and password:
            user = {
                'id': 1 if username == 'admin' else 2,
                'username': username,
                'role': '管理员' if username == 'admin' else '用户',
                'email': f'{username}@cyber-range.com'
            }
            return jsonify({
                'status': 'success',
                'msg': '登录成功',
                'user': user,
                'token': 'demo-token-' + username
            })
        
        return jsonify({
            'status': 'error',
            'msg': '用户名或密码不能为空'
        }), 400
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """用户登出"""
        return jsonify({
            'status': 'success',
            'msg': '登出成功'
        })
    
    @app.route('/api/auth/user', methods=['GET'])
    def get_user():
        """获取当前用户信息"""
        # 演示模式
        return jsonify({
            'status': 'success',
            'user': {
                'id': 1,
                'username': 'admin',
                'role': '管理员',
                'email': 'admin@cyber-range.com'
            }
        })
    
    # ==================== 统计接口 ====================
    @app.route('/api/stats/overview')
    def stats_overview():
        """获取统计概览"""
        return jsonify({
            'status': 'success',
            'data': {
                'total_environments': 5,
                'running_environments': 3,
                'attack_tasks': 12,
                'defense_rules': 8,
                'alerts': 3,
                'logs': 156
            }
        })
    
    @app.route('/api/stats/health')
    def stats_health():
        """获取系统健康度"""
        return jsonify({
            'status': 'success',
            'data': {
                'overall': 85,
                'cpu': 45,
                'memory': 62,
                'disk': 78,
                'network': 92
            }
        })
    
    @app.route('/api/stats/alerts')
    def stats_alerts():
        """获取告警统计"""
        return jsonify({
            'status': 'success',
            'data': [
                {'id': 1, 'level': 'high', 'type': '入侵检测', 'source': '192.168.1.100', 'time': datetime.now().isoformat(), 'status': '未处理'},
                {'id': 2, 'level': 'medium', 'type': '异常流量', 'source': '10.0.0.50', 'time': datetime.now().isoformat(), 'status': '已处理'},
                {'id': 3, 'level': 'low', 'type': '端口扫描', 'source': '172.16.0.25', 'time': datetime.now().isoformat(), 'status': '未处理'}
            ]
        })
    
    @app.route('/api/stats/recent-logs')
    def stats_recent_logs():
        """获取最近日志"""
        return jsonify({
            'status': 'success',
            'data': [
                {'id': 1, 'type': 'attack', 'action': 'SQL注入测试', 'target': 'Web服务器', 'time': datetime.now().isoformat(), 'status': 'success'},
                {'id': 2, 'type': 'defense', 'action': 'WAF规则更新', 'target': '防火墙', 'time': datetime.now().isoformat(), 'status': 'success'},
                {'id': 3, 'type': 'system', 'action': '容器启动', 'target': '靶场环境-1', 'time': datetime.now().isoformat(), 'status': 'success'}
            ]
        })
    
    # ==================== 环境管理接口 (匹配前端 /api/env/*) ====================
    @app.route('/api/env/list')
    def get_environments():
        """获取环境列表"""
        return jsonify({
            'status': 'success',
            'containers': [
                {'id': '1', 'target_id': 'target-1', 'name': 'Web靶场-1', 'image': 'nginx:latest', 'status': 'running', 'ports': '8080:80', 'created': datetime.now().strftime('%Y-%m-%d %H:%M')},
                {'id': '2', 'target_id': 'target-2', 'name': '数据库靶场-1', 'image': 'mysql:5.7', 'status': 'running', 'ports': '3306:3306', 'created': datetime.now().strftime('%Y-%m-%d %H:%M')},
                {'id': '3', 'target_id': 'target-3', 'name': 'API靶场-1', 'image': 'python:3.9', 'status': 'running', 'ports': '5000:5000', 'created': datetime.now().strftime('%Y-%m-%d %H:%M')},
                {'id': '4', 'target_id': 'target-4', 'name': '文件服务器靶场', 'image': 'ftp:latest', 'status': 'stopped', 'ports': '21:21', 'created': datetime.now().strftime('%Y-%m-%d %H:%M')},
                {'id': '5', 'target_id': 'target-5', 'name': '邮件服务器靶场', 'image': 'smtp:latest', 'status': 'stopped', 'ports': '25:25', 'created': datetime.now().strftime('%Y-%m-%d %H:%M')}
            ]
        })
    
    @app.route('/api/env/stats')
    def get_env_stats():
        """获取环境统计"""
        return jsonify({
            'status': 'success',
            'stats': {
                'total': 5,
                'running': 3,
                'stopped': 2,
                'created': 0
            }
        })
    
    @app.route('/api/env/images')
    def get_env_images():
        """获取可用镜像列表"""
        return jsonify({
            'status': 'success',
            'images': [
                {'value': 'nginx', 'label': 'Nginx Web服务器'},
                {'value': 'mysql:8.0', 'label': 'MySQL 8.0'},
                {'value': 'redis:alpine', 'label': 'Redis 缓存'},
                {'value': 'python:3.11-slim', 'label': 'Python 3.11'},
                {'value': 'ubuntu:22.04', 'label': 'Ubuntu 22.04'},
                {'value': 'dvwa', 'label': 'DVWA (漏洞靶场)'},
                {'value': 'wordpress:latest', 'label': 'WordPress'},
                {'value': 'php:8.1-apache', 'label': 'PHP 8.1 + Apache'},
                {'value': 'node:18-alpine', 'label': 'Node.js 18'}
            ]
        })
    
    @app.route('/api/env/create', methods=['POST'])
    def create_environment():
        """创建环境"""
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'container_id': 'demo-' + str(int(datetime.now().timestamp())),
            'name': data.get('name', '新环境'),
            'port': data.get('port', '8080'),
            'image': data.get('image', 'nginx')
        }), 201
    
    @app.route('/api/env/start/<container_id>', methods=['POST'])
    def start_environment(container_id):
        """启动环境"""
        return jsonify({
            'status': 'success',
            'msg': f'环境 {container_id} 启动成功'
        })
    
    @app.route('/api/env/stop/<container_id>', methods=['POST'])
    def stop_environment(container_id):
        """停止环境"""
        return jsonify({
            'status': 'success',
            'msg': f'环境 {container_id} 停止成功'
        })
    
    @app.route('/api/env/restart/<container_id>', methods=['POST'])
    def restart_environment(container_id):
        """重启环境"""
        return jsonify({
            'status': 'success',
            'msg': f'环境 {container_id} 重启成功'
        })
    
    @app.route('/api/env/delete/<container_id>', methods=['POST'])
    def delete_environment(container_id):
        """删除环境"""
        return jsonify({
            'status': 'success',
            'deleted': container_id
        })
    
    @app.route('/api/env/clean', methods=['POST'])
    def clean_environments():
        """批量清理环境"""
        return jsonify({
            'status': 'success',
            'cleaned': 0,
            'failed': []
        })
    
    # ==================== 攻击任务接口 (匹配前端 /api/attack/*) ====================
    @app.route('/api/attack/types')
    def get_attack_types():
        """获取攻击类型列表"""
        return jsonify({
            'status': 'success',
            'types': [
                {'value': 'SQL注入', 'label': 'SQL注入攻击'},
                {'value': 'XSS攻击', 'label': '跨站脚本攻击'},
                {'value': '命令执行', 'label': '命令执行攻击'},
                {'value': '端口扫描', 'label': '端口扫描'},
                {'value': '暴力破解', 'label': '暴力破解'},
                {'value': 'DDoS攻击', 'label': 'DDoS攻击'},
                {'value': '中间人攻击', 'label': '中间人攻击'},
                {'value': '文件包含', 'label': '文件包含漏洞'}
            ]
        })
    
    @app.route('/api/attack/list')
    def get_attacks():
        """获取攻击任务列表"""
        return jsonify({
            'status': 'success',
            'attacks': [
                {'attack_id': 'attack-1', 'name': 'SQL注入测试', 'attack_type': 'SQL注入', 'target': 'Web靶场-1', 'target_id': 'target-1', 'port': '80', 'intensity': 7, 'status': 'completed', 'created_at': datetime.now().isoformat()},
                {'attack_id': 'attack-2', 'name': 'XSS攻击测试', 'attack_type': 'XSS攻击', 'target': 'Web靶场-1', 'target_id': 'target-1', 'port': '80', 'intensity': 6, 'status': 'running', 'created_at': datetime.now().isoformat()},
                {'attack_id': 'attack-3', 'name': 'CSRF漏洞检测', 'attack_type': '命令执行', 'target': 'API靶场-1', 'target_id': 'target-3', 'port': '5000', 'intensity': 5, 'status': 'pending', 'created_at': datetime.now().isoformat()},
                {'attack_id': 'attack-4', 'name': '暴力破解测试', 'attack_type': '暴力破解', 'target': '数据库靶场-1', 'target_id': 'target-2', 'port': '3306', 'intensity': 8, 'status': 'blocked', 'created_at': datetime.now().isoformat()}
            ]
        })
    
    @app.route('/api/attack/stats')
    def get_attack_stats():
        """获取攻击统计"""
        return jsonify({
            'status': 'success',
            'stats': {
                'total': 12,
                'success': 5,
                'failed': 3,
                'blocked': 4
            },
            'user_stats': {
                'total': 4,
                'success': 1,
                'failed': 1,
                'running': 1
            }
        })
    
    @app.route('/api/attack/templates')
    def get_attack_templates():
        """获取攻击模板"""
        return jsonify({
            'status': 'success',
            'templates': [
                {
                    'name': 'Web应用渗透测试',
                    'attacks': [
                        {'name': 'SQL注入检测', 'type': 'SQL注入', 'target': '127.0.0.1', 'port': '80', 'intensity': 7},
                        {'name': 'XSS漏洞扫描', 'type': 'XSS攻击', 'target': '127.0.0.1', 'port': '80', 'intensity': 6}
                    ]
                },
                {
                    'name': '网络扫描',
                    'attacks': [
                        {'name': '端口扫描', 'type': '端口扫描', 'target': '127.0.0.1', 'port': '1-1000', 'intensity': 8}
                    ]
                }
            ]
        })
    
    @app.route('/api/attack/create', methods=['POST'])
    def create_attack():
        """创建攻击任务"""
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'attack': {
                'attack_id': 'attack-' + str(int(datetime.now().timestamp())),
                'name': data.get('name', '新攻击任务'),
                'attack_type': data.get('attack_type', 'SQL注入'),
                'target': data.get('target', '127.0.0.1'),
                'port': data.get('port', '80'),
                'intensity': data.get('intensity', 5),
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
        }), 201
    
    @app.route('/api/attack/execute/<attack_id>', methods=['POST'])
    def execute_attack(attack_id):
        """执行攻击"""
        return jsonify({
            'status': 'success',
            'task_id': f'attack_{attack_id}_{int(datetime.now().timestamp())}',
            'message': '攻击任务已加入队列'
        })
    
    @app.route('/api/attack/result/<attack_id>')
    def get_attack_result(attack_id):
        """获取攻击结果"""
        return jsonify({
            'status': 'success',
            'attack': {
                'attack_id': attack_id,
                'status': 'completed',
                'result': {
                    'success': True,
                    'blocked': False,
                    'message': '发现2个漏洞'
                }
            },
            'result': {
                'success': True,
                'blocked': False,
                'message': '发现2个漏洞',
                'vulnerabilities': [
                    {'type': 'SQL注入', 'severity': 'high', 'location': '/api/users?id=1', 'description': '存在SQL注入漏洞'},
                    {'type': '信息泄露', 'severity': 'medium', 'location': '/api/config', 'description': '敏感信息暴露'}
                ]
            }
        })
    
    @app.route('/api/attack/batch-execute', methods=['POST'])
    def batch_execute_attacks():
        """批量执行攻击"""
        return jsonify({
            'status': 'success',
            'tasks': ['task-1', 'task-2'],
            'message': '成功添加 2 个攻击任务到队列'
        })
    
    # ==================== 防御规则接口 (匹配前端 /api/defense/*) ====================
    @app.route('/api/defense/types')
    def get_defense_types():
        """获取防御类型列表"""
        return jsonify({
            'status': 'success',
            'types': [
                {'value': 'WAF', 'label': 'Web应用防火墙'},
                {'value': 'IDS', 'label': '入侵检测系统'},
                {'value': 'IPS', 'label': '入侵防御系统'},
                {'value': '防火墙', 'label': '网络防火墙'},
                {'value': '蜜罐', 'label': '蜜罐系统'},
                {'value': '入侵检测', 'label': '入侵检测'}
            ]
        })
    
    @app.route('/api/defense/list')
    def get_defenses():
        """获取防御规则列表"""
        return jsonify({
            'status': 'success',
            'defenses': [
                {'defense_id': 'defense-1', 'name': 'WAF规则-1', 'defense_type': 'WAF', 'description': 'Web应用防火墙', 'enabled': True, 'coverage': 92.0, 'status': 'active', 'created_at': datetime.now().isoformat()},
                {'defense_id': 'defense-2', 'name': 'IDS规则-1', 'defense_type': 'IDS', 'description': '入侵检测系统', 'enabled': True, 'coverage': 85.0, 'status': 'active', 'created_at': datetime.now().isoformat()},
                {'defense_id': 'defense-3', 'name': 'IPS规则-1', 'defense_type': 'IPS', 'description': '入侵防御系统', 'enabled': True, 'coverage': 78.0, 'status': 'active', 'created_at': datetime.now().isoformat()},
                {'defense_id': 'defense-4', 'name': '蜜罐-1', 'defense_type': '蜜罐', 'description': '蜜罐系统', 'enabled': False, 'coverage': 0.0, 'status': 'inactive', 'created_at': datetime.now().isoformat()}
            ]
        })
    
    @app.route('/api/defense/stats')
    def get_defense_stats():
        """获取防御统计"""
        return jsonify({
            'status': 'success',
            'stats': {
                'total': 8,
                'enabled': 6,
                'disabled': 2,
                'avg_coverage': 75.5
            },
            'user_stats': {
                'total': 4,
                'enabled': 3,
                'disabled': 1,
                'avg_coverage': 63.75
            }
        })
    
    @app.route('/api/defense/templates')
    def get_defense_templates():
        """获取防御模板"""
        return jsonify({
            'status': 'success',
            'templates': [
                {
                    'name': 'Web应用安全防护',
                    'defenses': [
                        {'name': 'SQL注入防护', 'type': 'WAF', 'description': '检测并阻止SQL注入攻击', 'coverage': 92.0},
                        {'name': 'XSS攻击拦截', 'type': 'WAF', 'description': '检测并阻止跨站脚本攻击', 'coverage': 88.0}
                    ]
                },
                {
                    'name': '网络安全防护',
                    'defenses': [
                        {'name': '端口扫描检测', 'type': 'IDS', 'description': '检测端口扫描行为', 'coverage': 95.0},
                        {'name': '暴力破解阻断', 'type': 'IPS', 'description': '阻止暴力破解攻击', 'coverage': 78.0}
                    ]
                }
            ]
        })
    
    @app.route('/api/defense/create', methods=['POST'])
    def create_defense():
        """创建防御规则"""
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'defense': {
                'defense_id': 'defense-' + str(int(datetime.now().timestamp())),
                'name': data.get('name', '新防御规则'),
                'defense_type': data.get('defense_type', 'WAF'),
                'description': data.get('description', ''),
                'enabled': data.get('enabled', True),
                'coverage': data.get('coverage', 50.0),
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
        }), 201
    
    @app.route('/api/defense/update/<defense_id>', methods=['PUT'])
    def update_defense(defense_id):
        """更新防御规则"""
        return jsonify({
            'status': 'success',
            'msg': '防御规则更新成功',
            'defense': {
                'defense_id': defense_id,
                'status': 'updated'
            }
        })
    
    @app.route('/api/defense/toggle/<defense_id>', methods=['POST'])
    def toggle_defense(defense_id):
        """切换防御规则状态"""
        return jsonify({
            'status': 'success',
            'defense': {
                'defense_id': defense_id,
                'enabled': True,
                'status': 'active'
            },
            'message': '防御规则已启用'
        })
    
    @app.route('/api/defense/delete/<defense_id>', methods=['DELETE'])
    def delete_defense(defense_id):
        """删除防御规则"""
        return jsonify({
            'status': 'success',
            'message': '防御规则已删除'
        })
    
    @app.route('/api/defense/check', methods=['POST'])
    def check_defense():
        """检查防御规则"""
        return jsonify({
            'status': 'success',
            'task_id': 'defense-check-' + str(int(datetime.now().timestamp())),
            'message': '防御检查任务已加入队列'
        })
    
    @app.route('/api/defense/result/<defense_id>')
    def get_defense_result(defense_id):
        """获取防御检查结果"""
        return jsonify({
            'status': 'success',
            'defense': {
                'defense_id': defense_id,
                'status': 'active'
            },
            'result': {
                'blocked': True,
                'message': '成功拦截攻击'
            }
        })
    
    # ==================== 日志接口 (匹配前端 /api/logs/*) ====================
    @app.route('/api/logs/list')
    def get_logs():
        """获取日志列表"""
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        level = request.args.get('level', '')
        source = request.args.get('source', '')
        
        logs = []
        for i in range(min(limit, 20)):
            logs.append({
                'log_id': 'log-' + str(offset + i + 1),
                'level': ['info', 'warning', 'danger', 'success'][i % 4],
                'source': ['attack', 'defense', 'target', 'system'][i % 4],
                'message': ['SQL注入检测完成', 'WAF拦截攻击', '容器启动成功', '系统健康检查'][i % 4],
                'target_id': 'target-' + str(i % 3 + 1),
                'user_id': 1,
                'created_at': datetime.now().isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': 156
        })
    
    @app.route('/api/logs/stats')
    def get_logs_stats():
        """获取日志统计"""
        return jsonify({
            'status': 'success',
            'stats': {
                'total': 156,
                'today': 12,
                'level_counts': {'info': 89, 'warning': 42, 'danger': 15, 'success': 10},
                'source_counts': {'attack': 45, 'defense': 38, 'target': 52, 'system': 21}
            },
            'user_stats': {
                'total': 25,
                'today': 3,
                'level_counts': {'info': 15, 'warning': 5, 'danger': 2, 'success': 3},
                'source_counts': {'attack': 10, 'defense': 8, 'target': 5, 'system': 2}
            }
        })
    
    @app.route('/api/logs/attack')
    def get_attack_logs():
        """获取攻击日志"""
        limit = int(request.args.get('limit', 50))
        return jsonify({
            'status': 'success',
            'logs': [
                {'log_id': 'attack-log-1', 'level': 'danger', 'source': 'attack', 'message': 'SQL注入攻击成功', 'created_at': datetime.now().isoformat()},
                {'log_id': 'attack-log-2', 'level': 'warning', 'source': 'attack', 'message': 'XSS攻击被拦截', 'created_at': datetime.now().isoformat()}
            ],
            'total': 45
        })
    
    @app.route('/api/logs/defense')
    def get_defense_logs():
        """获取防御日志"""
        limit = int(request.args.get('limit', 50))
        return jsonify({
            'status': 'success',
            'logs': [
                {'log_id': 'defense-log-1', 'level': 'success', 'source': 'defense', 'message': 'WAF规则更新成功', 'created_at': datetime.now().isoformat()},
                {'log_id': 'defense-log-2', 'level': 'info', 'source': 'defense', 'message': 'IDS检测到异常流量', 'created_at': datetime.now().isoformat()}
            ],
            'total': 38
        })
    
    @app.route('/api/logs/system')
    def get_system_logs():
        """获取系统日志"""
        limit = int(request.args.get('limit', 50))
        return jsonify({
            'status': 'success',
            'logs': [
                {'log_id': 'sys-log-1', 'level': 'info', 'source': 'system', 'message': '系统启动完成', 'created_at': datetime.now().isoformat()},
                {'log_id': 'sys-log-2', 'level': 'info', 'source': 'system', 'message': '数据库连接成功', 'created_at': datetime.now().isoformat()}
            ],
            'total': 52
        })
    
    @app.route('/api/logs/docker')
    def get_docker_logs():
        """获取Docker日志"""
        limit = int(request.args.get('limit', 50))
        return jsonify({
            'status': 'success',
            'logs': [
                {'log_id': 'docker-log-1', 'level': 'info', 'source': 'docker', 'message': '容器web-1启动', 'created_at': datetime.now().isoformat()},
                {'log_id': 'docker-log-2', 'level': 'info', 'source': 'docker', 'message': '容器db-1运行正常', 'created_at': datetime.now().isoformat()}
            ],
            'total': 30
        })
    
    @app.route('/api/logs/watchdog/status')
    def get_watchdog_status():
        """获取监控服务状态"""
        return jsonify({
            'status': 'success',
            'watchdog': {
                'running': True,
                'uptime': 3600,
                'checks_performed': 156,
                'alerts_generated': 3,
                'last_check': datetime.now().isoformat()
            }
        })
    
    @app.route('/api/logs/watchdog/start', methods=['POST'])
    def start_watchdog():
        """启动监控服务"""
        return jsonify({
            'status': 'success',
            'message': '监控服务已启动'
        })
    
    @app.route('/api/logs/watchdog/stop', methods=['POST'])
    def stop_watchdog():
        """停止监控服务"""
        return jsonify({
            'status': 'success',
            'message': '监控服务已停止'
        })
    
    @app.route('/api/logs/watchdog/clear', methods=['POST'])
    def clear_watchdog_stats():
        """清空监控统计"""
        return jsonify({
            'status': 'success',
            'message': '监控统计已清空'
        })
    
    @app.route('/api/logs/search')
    def search_logs():
        """搜索日志"""
        keyword = request.args.get('keyword', '')
        return jsonify({
            'status': 'success',
            'logs': [
                {'log_id': 'search-1', 'level': 'info', 'source': 'system', 'message': f'搜索结果: {keyword}', 'created_at': datetime.now().isoformat()}
            ],
            'total': 1,
            'keyword': keyword
        })
    
    @app.route('/api/logs/export', methods=['POST'])
    def export_logs():
        """导出日志"""
        return jsonify({
            'status': 'success',
            'msg': '日志导出成功',
            'file': 'logs_export_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
        })
    
    @app.route('/api/logs/clear', methods=['POST'])
    def clear_logs():
        """清理日志"""
        return jsonify({
            'status': 'success',
            'message': '日志清理成功',
            'cleared_count': 0
        })
    
    # ==================== AI决策接口 ====================
    @app.route('/api/ai/analyze', methods=['POST'])
    def ai_analyze():
        """AI威胁分析"""
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'data': {
                'threat_level': 'medium',
                'threat_type': 'SQL注入攻击',
                'confidence': 0.85,
                'analysis': '检测到可疑的SQL注入尝试，攻击者试图通过未过滤的输入参数执行恶意SQL语句。',
                'affected_systems': ['Web服务器', '数据库服务器'],
                'recommendations': [
                    '立即启用WAF规则拦截SQL注入',
                    '检查数据库访问日志',
                    '更新输入验证规则',
                    '通知安全团队进行人工审查'
                ],
                'timestamp': datetime.now().isoformat()
            }
        })
    
    @app.route('/api/ai/recommend', methods=['POST'])
    def ai_recommend():
        """AI防御建议"""
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': [
                    {'priority': 'high', 'action': '启用IPS规则', 'description': '阻止已知的攻击模式', 'impact': '可能影响正常流量'},
                    {'priority': 'medium', 'action': '更新WAF规则', 'description': '添加新的SQL注入检测规则', 'impact': '低'},
                    {'priority': 'low', 'action': '部署蜜罐', 'description': '诱捕攻击者收集情报', 'impact': '需要额外资源'}
                ],
                'auto_defense_available': True,
                'estimated_risk_reduction': 75,
                'timestamp': datetime.now().isoformat()
            }
        })
    
    @app.route('/api/ai/history')
    def ai_history():
        """获取AI分析历史"""
        return jsonify({
            'status': 'success',
            'data': [
                {'id': 1, 'type': 'threat_analysis', 'input': 'SQL注入攻击', 'result': '高风险', 'time': datetime.now().isoformat()},
                {'id': 2, 'type': 'defense_recommend', 'input': 'WAF配置', 'result': '3条建议', 'time': datetime.now().isoformat()},
                {'id': 3, 'type': 'threat_analysis', 'input': '异常流量', 'result': '中风险', 'time': datetime.now().isoformat()}
            ]
        })
    
    @app.route('/api/ai/auto-defense', methods=['POST'])
    def ai_auto_defense():
        """AI自动防御"""
        return jsonify({
            'status': 'success',
            'msg': '自动防御已启动',
            'data': {
                'actions_taken': ['WAF规则已更新', 'IPS已启用', '告警已发送'],
                'status': 'active'
            }
        })
    
    # ==================== 拓扑接口 ====================
    @app.route('/api/topology')
    def get_topology():
        """获取网络拓扑"""
        return jsonify({
            'status': 'success',
            'data': {
                'nodes': [
                    {'id': 'gateway', 'name': '网关', 'type': 'gateway', 'ip': '192.168.1.1', 'status': 'online', 'x': 400, 'y': 50},
                    {'id': 'firewall', 'name': '防火墙', 'type': 'firewall', 'ip': '192.168.1.2', 'status': 'online', 'x': 400, 'y': 150},
                    {'id': 'web1', 'name': 'Web靶场-1', 'type': 'web', 'ip': '192.168.1.100', 'status': 'online', 'x': 200, 'y': 250},
                    {'id': 'web2', 'name': 'Web靶场-2', 'type': 'web', 'ip': '192.168.1.101', 'status': 'online', 'x': 600, 'y': 250},
                    {'id': 'db1', 'name': '数据库靶场', 'type': 'database', 'ip': '192.168.1.102', 'status': 'online', 'x': 200, 'y': 350},
                    {'id': 'api1', 'name': 'API靶场', 'type': 'api', 'ip': '192.168.1.103', 'status': 'offline', 'x': 600, 'y': 350},
                    {'id': 'honeypot', 'name': '蜜罐', 'type': 'honeypot', 'ip': '192.168.1.200', 'status': 'online', 'x': 400, 'y': 450}
                ],
                'edges': [
                    {'source': 'gateway', 'target': 'firewall'},
                    {'source': 'firewall', 'target': 'web1'},
                    {'source': 'firewall', 'target': 'web2'},
                    {'source': 'web1', 'target': 'db1'},
                    {'source': 'web2', 'target': 'api1'},
                    {'source': 'firewall', 'target': 'honeypot'}
                ]
            }
        })
    
    @app.route('/api/topology/ping', methods=['POST'])
    def topology_ping():
        """Ping测试"""
        data = request.get_json() or {}
        ip = data.get('ip', '')
        return jsonify({
            'status': 'success',
            'data': {
                'ip': ip,
                'reachable': True,
                'latency': 15,
                'time': datetime.now().isoformat()
            }
        })
    
    @app.route('/api/topology/ssh', methods=['POST'])
    def topology_ssh():
        """SSH连接测试"""
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'data': {
                'host': data.get('host', ''),
                'connected': True,
                'message': 'SSH连接成功'
            }
        })
    
    @app.route('/api/topology/update', methods=['POST'])
    def topology_update():
        """更新拓扑"""
        return jsonify({
            'status': 'success',
            'msg': '拓扑更新成功'
        })
    
    # ==================== 错误处理 ====================
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'msg': '接口不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {error}")
        return jsonify({
            'status': 'error',
            'msg': '内部服务器错误'
        }), 500
    
    # 请求日志
    @app.before_request
    def before_request():
        logger.info(f"请求: {request.method} {request.path}")
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("AI攻防靶场管理系统 - 后端服务启动")
    logger.info("=" * 50)
    logger.info("服务地址: http://localhost:5000")
    logger.info("API文档: http://localhost:5000/api/health")
    
    # 检测运行模式
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    
    if db_user and db_pass and db_user != 'root' and db_pass != 'your_password':
        logger.info("模式: ✅ 真实模式 (已连接数据库)")
        
        # 初始化数据库
        try:
            from services.database import db_service
            if db_service.init_database():
                logger.info("✅ 数据库初始化完成")
        except Exception as e:
            logger.warning(f"⚠️  数据库初始化: {e}")
    else:
        logger.info("模式: 📌 演示模式 (无需数据库)")
        
    logger.info("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
