# -*- coding: utf-8 -*-
"""
防御模拟Agent - 检测和阻止攻击
"""
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

from models.defense import Defense
from models.log import Log
from models.attack import Attack
from services.database import db_service

logger = logging.getLogger('agents.defense')


class DefenseAgent:
    """防御模拟Agent - 检测和阻止攻击"""
    
    def __init__(self):
        # 初始化防御规则
        self.defense_rules = self._load_defense_rules()
        self.active_monitors = {}
    
    def _load_defense_rules(self):
        """加载防御规则"""
        rules = {
            'waf_rules': {
                'sql_injection': {
                    'patterns': ["'", '"', 'UNION', 'SELECT', 'INSERT', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'EXEC', 'xp_', 'sp_'],
                    'severity': 'high',
                    'action': 'block'
                },
                'xss': {
                    'patterns': ['<script', 'javascript:', 'onerror', 'onload', 'onclick', 'alert('],
                    'severity': 'medium',
                    'action': 'sanitize'
                },
                'command_injection': {
                    'patterns': [';', '|', '&', '`', '$(', 'eval', 'exec'],
                    'severity': 'high',
                    'action': 'block'
                }
            },
            'ids_rules': {
                'port_scan': {
                    'threshold': 10,  # 10秒内超过10次连接
                    'time_window': 10,
                    'severity': 'medium',
                    'action': 'alert'
                },
                'brute_force': {
                    'threshold': 5,  # 5分钟内5次失败登录
                    'time_window': 300,
                    'severity': 'high',
                    'action': 'block_ip'
                }
            }
        }
        return rules
    
    def detect_attack(self, attack_data, target_id=None, user_id=None):
        """检测攻击"""
        try:
            attack_type = attack_data.get('attack_type', 'unknown')
            attack_payload = attack_data.get('payload', '')
            source_ip = attack_data.get('source_ip', 'unknown')
            
            # 根据攻击类型进行检测
            detection_result = self._analyze_attack(attack_type, attack_payload, source_ip)
            
            # 记录检测日志
            Log.create('info', 'defense', f'攻击检测: {attack_type}, 结果: {detection_result["status"]}', user_id=user_id)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"攻击检测失败: {e}")
            return {
                'status': 'error',
                'msg': f'检测失败: {str(e)}'
            }
    
    def _analyze_attack(self, attack_type, attack_payload, source_ip):
        """分析攻击"""
        # 根据攻击类型应用不同检测规则
        if attack_type == 'SQL Injection':
            return self._detect_sql_injection(attack_payload)
        elif attack_type == 'XSS':
            return self._detect_xss(attack_payload)
        elif attack_type == 'Command Injection':
            return self._detect_command_injection(attack_payload)
        elif attack_type == 'Port Scan':
            return self._detect_port_scan(source_ip)
        elif attack_type == 'Brute Force':
            return self._detect_brute_force(source_ip)
        else:
            # 通用检测
            return self._generic_detection(attack_type, attack_payload)
    
    def _detect_sql_injection(self, payload):
        """检测SQL注入"""
        try:
            # 使用AI模型进行智能检测
            from llm.local_model import LocalLLM
            llm = LocalLLM()
            
            prompt = f"""
            请分析以下输入是否包含SQL注入攻击载荷：
            
            输入内容：{payload}
            
            请返回一个JSON对象，包含以下字段：
            - is_attack: 是否为攻击载荷 (boolean)
            - attack_type: 攻击类型 (string)
            - severity: 严重程度 (low/medium/high/critical)
            - confidence: 置信度 (0-1)
            - detected_patterns: 检测到的模式列表
            - explanation: 检测说明
            
            只返回JSON内容，不要其他文字。
            """
            
            result = llm.chat(prompt)
            import json
            ai_result = json.loads(result['content'].strip())
            
            if ai_result['is_attack']:
                return {
                    'status': 'detected',
                    'severity': ai_result['severity'],
                    'action': 'block',
                    'threat_type': ai_result['attack_type'],
                    'detected_patterns': ai_result['detected_patterns'],
                    'confidence': ai_result['confidence'] * 100,
                    'explanation': ai_result['explanation']
                }
            else:
                return {
                    'status': 'clean',
                    'msg': '未检测到SQL注入特征'
                }
                
        except Exception as e:
            # 如果AI检测失败，回退到规则引擎
            logger.warning(f"AI SQL注入检测失败，使用规则引擎: {e}")
            waf_rules = self.defense_rules['waf_rules']['sql_injection']
            
            detected_patterns = []
            for pattern in waf_rules['patterns']:
                if pattern.lower() in payload.lower():
                    detected_patterns.append(pattern)
            
            if detected_patterns:
                return {
                    'status': 'detected',
                    'severity': waf_rules['severity'],
                    'action': waf_rules['action'],
                    'threat_type': 'SQL Injection',
                    'detected_patterns': detected_patterns,
                    'confidence': min(95, len(detected_patterns) * 25)  # 置信度计算
                }
            else:
                return {
                    'status': 'clean',
                    'msg': '未检测到SQL注入特征'
                }
    
    def _detect_xss(self, payload):
        """检测XSS"""
        try:
            # 使用AI模型进行智能检测
            from llm.local_model import LocalLLM
            llm = LocalLLM()
            
            prompt = f"""
            请分析以下输入是否包含XSS攻击载荷：
            
            输入内容：{payload}
            
            请返回一个JSON对象，包含以下字段：
            - is_attack: 是否为攻击载荷 (boolean)
            - attack_type: 攻击类型 (string)
            - severity: 严重程度 (low/medium/high/critical)
            - confidence: 置信度 (0-1)
            - detected_patterns: 检测到的模式列表
            - explanation: 检测说明
            
            只返回JSON内容，不要其他文字。
            """
            
            result = llm.chat(prompt)
            import json
            ai_result = json.loads(result['content'].strip())
            
            if ai_result['is_attack']:
                return {
                    'status': 'detected',
                    'severity': ai_result['severity'],
                    'action': 'sanitize',
                    'threat_type': ai_result['attack_type'],
                    'detected_patterns': ai_result['detected_patterns'],
                    'confidence': ai_result['confidence'] * 100,
                    'explanation': ai_result['explanation']
                }
            else:
                return {
                    'status': 'clean',
                    'msg': '未检测到XSS特征'
                }
                
        except Exception as e:
            # 如果AI检测失败，回退到规则引擎
            logger.warning(f"AI XSS检测失败，使用规则引擎: {e}")
            waf_rules = self.defense_rules['waf_rules']['xss']
            
            detected_patterns = []
            for pattern in waf_rules['patterns']:
                if pattern.lower() in payload.lower():
                    detected_patterns.append(pattern)
            
            if detected_patterns:
                return {
                    'status': 'detected',
                    'severity': waf_rules['severity'],
                    'action': waf_rules['action'],
                    'threat_type': 'XSS',
                    'detected_patterns': detected_patterns,
                    'confidence': min(90, len(detected_patterns) * 20)
                }
            else:
                return {
                    'status': 'clean',
                    'msg': '未检测到XSS特征'
                }
    
    def _detect_command_injection(self, payload):
        """检测命令注入"""
        try:
            # 使用AI模型进行智能检测
            from llm.local_model import LocalLLM
            llm = LocalLLM()
            
            prompt = f"""
            请分析以下输入是否包含命令注入攻击载荷：
            
            输入内容：{payload}
            
            请返回一个JSON对象，包含以下字段：
            - is_attack: 是否为攻击载荷 (boolean)
            - attack_type: 攻击类型 (string)
            - severity: 严重程度 (low/medium/high/critical)
            - confidence: 置信度 (0-1)
            - detected_patterns: 检测到的模式列表
            - explanation: 检测说明
            
            只返回JSON内容，不要其他文字。
            """
            
            result = llm.chat(prompt)
            import json
            ai_result = json.loads(result['content'].strip())
            
            if ai_result['is_attack']:
                return {
                    'status': 'detected',
                    'severity': ai_result['severity'],
                    'action': 'block',
                    'threat_type': ai_result['attack_type'],
                    'detected_patterns': ai_result['detected_patterns'],
                    'confidence': ai_result['confidence'] * 100,
                    'explanation': ai_result['explanation']
                }
            else:
                return {
                    'status': 'clean',
                    'msg': '未检测到命令注入特征'
                }
                
        except Exception as e:
            # 如果AI检测失败，回退到规则引擎
            logger.warning(f"AI命令注入检测失败，使用规则引擎: {e}")
            waf_rules = self.defense_rules['waf_rules']['command_injection']
            
            detected_patterns = []
            for pattern in waf_rules['patterns']:
                if pattern in payload:
                    detected_patterns.append(pattern)
            
            if detected_patterns:
                return {
                    'status': 'detected',
                    'severity': waf_rules['severity'],
                    'action': waf_rules['action'],
                    'threat_type': 'Command Injection',
                    'detected_patterns': detected_patterns,
                    'confidence': min(98, len(detected_patterns) * 30)
                }
            else:
                return {
                    'status': 'clean',
                    'msg': '未检测到命令注入特征'
                }
    
    def _detect_port_scan(self, source_ip):
        """检测端口扫描"""
        ids_rules = self.defense_rules['ids_rules']['port_scan']
        
        # 模拟检测逻辑（实际应检查连接频率）
        # 这里简化处理，随机判断
        if random.random() > 0.7:  # 30%概率检测到端口扫描
            return {
                'status': 'detected',
                'severity': ids_rules['severity'],
                'action': ids_rules['action'],
                'threat_type': 'Port Scan',
                'confidence': 85
            }
        else:
            return {
                'status': 'clean',
                'msg': '未检测到端口扫描行为'
            }
    
    def _detect_brute_force(self, source_ip):
        """检测暴力破解"""
        ids_rules = self.defense_rules['ids_rules']['brute_force']
        
        # 模拟检测逻辑（实际应检查登录失败频率）
        if random.random() > 0.8:  # 20%概率检测到暴力破解
            return {
                'status': 'detected',
                'severity': ids_rules['severity'],
                'action': ids_rules['action'],
                'threat_type': 'Brute Force',
                'confidence': 90
            }
        else:
            return {
                'status': 'clean',
                'msg': '未检测到暴力破解行为'
            }
    
    def _generic_detection(self, attack_type, payload):
        """通用检测"""
        # 随机检测结果（实际应使用更复杂的检测逻辑）
        detection_chance = random.random()
        
        if detection_chance > 0.6:  # 40%概率检测到威胁
            return {
                'status': 'detected',
                'severity': 'medium',
                'action': 'monitor',
                'threat_type': attack_type,
                'confidence': int(detection_chance * 100)
            }
        else:
            return {
                'status': 'clean',
                'msg': f'未检测到{attack_type}威胁特征'
            }
    
    def apply_defense(self, threat_info, user_id=None):
        """应用防御措施"""
        try:
            threat_type = threat_info.get('threat_type', 'unknown')
            action = threat_info.get('action', 'monitor')
            source_ip = threat_info.get('source_ip', 'unknown')
            
            # 根据威胁类型和行动方案执行防御
            defense_result = self._execute_defense_action(threat_type, action, source_ip)
            
            # 记录防御日志
            Log.create('info', 'defense', f'防御措施执行: {action} for {threat_type}', user_id=user_id)
            
            return defense_result
            
        except Exception as e:
            logger.error(f"应用防御失败: {e}")
            return {
                'status': 'error',
                'msg': f'防御应用失败: {str(e)}'
            }
    
    def _execute_defense_action(self, threat_type, action, source_ip):
        """执行防御行动"""
        if action == 'block':
            return self._block_request(threat_type, source_ip)
        elif action == 'block_ip':
            return self._block_ip(source_ip)
        elif action == 'sanitize':
            return self._sanitize_input(threat_type)
        elif action == 'alert':
            return self._generate_alert(threat_type, source_ip)
        elif action == 'monitor':
            return self._start_monitoring(threat_type, source_ip)
        else:
            return {
                'status': 'applied',
                'msg': f'未知行动类型 {action}，已记录威胁',
                'action_taken': 'logged'
            }
    
    def _block_request(self, threat_type, source_ip):
        """阻止请求"""
        return {
            'status': 'blocked',
            'action': 'request_blocked',
            'msg': f'已阻止{threat_type}请求',
            'blocked_ip': source_ip
        }
    
    def _block_ip(self, source_ip):
        """封禁IP"""
        # 在实际系统中，这里会将IP添加到防火墙黑名单
        return {
            'status': 'blocked',
            'action': 'ip_blocked',
            'msg': f'已封禁IP地址: {source_ip}',
            'blocked_ip': source_ip
        }
    
    def _sanitize_input(self, threat_type):
        """净化输入"""
        return {
            'status': 'sanitized',
            'action': 'input_sanitized',
            'msg': f'已净化{threat_type}输入',
            'method': 'input_validation_and_encoding'
        }
    
    def _generate_alert(self, threat_type, source_ip):
        """生成告警"""
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        
        # 创建告警日志
        Log.create('warning', 'defense', f'威胁告警: {threat_type} from {source_ip}', 
                  details={'alert_id': alert_id, 'threat_type': threat_type})
        
        return {
            'status': 'alerted',
            'action': 'alert_generated',
            'msg': f'已生成{threat_type}告警',
            'alert_id': alert_id
        }
    
    def _start_monitoring(self, threat_type, source_ip):
        """开始监控"""
        monitor_id = f"monitor_{uuid.uuid4().hex[:8]}"
        self.active_monitors[monitor_id] = {
            'threat_type': threat_type,
            'source_ip': source_ip,
            'start_time': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return {
            'status': 'monitoring',
            'action': 'monitoring_started',
            'msg': f'开始监控{threat_type}',
            'monitor_id': monitor_id
        }
    
    def deploy_defense_system(self, defense_type, config=None, user_id=None):
        """部署防御系统"""
        try:
            # 创建防御规则
            defense = Defense(
                name=f"{defense_type}_defense_{uuid.uuid4().hex[:8]}",
                defense_type=defense_type,
                description=f"自动部署的{defense_type}防御系统",
                enabled=1,
                coverage=85,  # 默认85%覆盖率
                config=json.dumps(config or {})
            )
            defense.save()
            
            # 记录部署日志
            Log.create('info', 'defense', f'部署防御系统: {defense.name}', user_id=user_id)
            
            return {
                'status': 'success',
                'defense_id': defense.defense_id,
                'defense_name': defense.name,
                'msg': f'{defense_type}防御系统部署成功'
            }
            
        except Exception as e:
            logger.error(f"部署防御系统失败: {e}")
            return {
                'status': 'error',
                'msg': f'部署失败: {str(e)}'
            }
    
    def analyze_logs_for_threats(self, log_data, user_id=None):
        """分析日志中的威胁"""
        try:
            # 使用AI模型进行智能日志分析
            try:
                from llm.local_model import LocalLLM
                llm = LocalLLM()
                
                # 准备日志数据供AI分析
                log_text = "\n".join([
                    f"[{entry.get('timestamp', entry.get('created_at', 'Unknown'))}] "
                    f"{entry.get('level', 'INFO')} - {entry.get('message', '')}"
                    for entry in log_data[:50]  # 限制分析的日志数量以提高性能
                ])
                
                prompt = f"""
                请分析以下系统日志，识别其中的安全威胁：
                
                日志内容：
                {log_text}
                
                请返回一个JSON对象，包含以下字段：
                - threats_detected: 检测到的威胁列表，每个威胁包含：
                  - type: 威胁类型
                  - severity: 严重程度 (low/medium/high/critical)
                  - confidence: 置信度 (0-1)
                  - description: 威胁描述
                  - timestamp: 时间戳
                  - related_logs: 相关日志条目
                - summary: 分析摘要
                - recommendations: 安全建议
                
                只返回JSON内容，不要其他文字。
                """
                
                result = llm.chat(prompt)
                import json
                ai_analysis = json.loads(result['content'].strip())
                
                # 记录分析结果
                Log.create('info', 'defense', f'AI日志分析完成，发现 {len(ai_analysis.get("threats_detected", []))} 个潜在威胁', user_id=user_id)
                
                return {
                    'status': 'analyzed',
                    'threats_detected': ai_analysis.get('threats_detected', []),
                    'total_logs_analyzed': len(log_data),
                    'summary': ai_analysis.get('summary', ''),
                    'recommendations': ai_analysis.get('recommendations', []),
                    'msg': f'AI分析发现 {len(ai_analysis.get("threats_detected", []))} 个潜在威胁'
                }
                
            except Exception as ai_error:
                # 如果AI分析失败，回退到规则引擎
                logger.warning(f"AI日志分析失败，使用规则引擎: {ai_error}")
                
                threats_detected = []
                
                # 分析日志数据寻找威胁指标
                for log_entry in log_data:
                    log_msg = log_entry.get('message', '').lower()
                    log_level = log_entry.get('level', 'info')
                    
                    # 检查各种威胁模式
                    if any(pattern in log_msg for pattern in ['sql', 'error', 'exception', 'failed', 'denied']):
                        if any(suspicious in log_msg for suspicious in ['union', 'select', 'drop', 'exec', 'eval']):
                            threats_detected.append({
                                'type': 'Potential SQL Injection',
                                'severity': 'high',
                                'log_entry': log_entry,
                                'confidence': 85
                            })
                    
                    if any(xss_pattern in log_msg for xss_pattern in ['<script', 'javascript:', 'alert(']):
                        threats_detected.append({
                            'type': 'Potential XSS',
                            'severity': 'medium',
                            'log_entry': log_entry,
                            'confidence': 75
                        })
                    
                    if 'connection' in log_msg and ('failed' in log_msg or 'denied' in log_msg):
                        # 检查是否是频繁连接尝试
                        threats_detected.append({
                            'type': 'Potential Scanning Activity',
                            'severity': 'low',
                            'log_entry': log_entry,
                            'confidence': 60
                        })
                
                # 记录分析结果
                Log.create('info', 'defense', f'规则引擎日志分析完成，发现 {len(threats_detected)} 个潜在威胁', user_id=user_id)
                
                return {
                    'status': 'analyzed',
                    'threats_detected': threats_detected,
                    'total_logs_analyzed': len(log_data),
                    'msg': f'规则引擎发现 {len(threats_detected)} 个潜在威胁'
                }
             
        except Exception as e:
            logger.error(f"日志分析失败: {e}")
            return {
                'status': 'error',
                'msg': f'日志分析失败: {str(e)}'
            }
    
    def get_active_defenses(self):
        """获取活跃防御"""
        try:
            # 从数据库获取启用的防御规则
            active_defenses = Defense.list_all(enabled=1)
            
            return {
                'status': 'success',
                'defenses': [defense.to_dict() for defense in active_defenses],
                'count': len(active_defenses)
            }
        except Exception as e:
            logger.error(f"获取活跃防御失败: {e}")
            return {
                'status': 'error',
                'msg': f'获取活跃防御失败: {str(e)}'
            }


# 全局实例
defense_agent = DefenseAgent()