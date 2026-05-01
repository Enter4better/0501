# -*- coding: utf-8 -*-
"""
攻击记录模型 - SQLite实现
"""
import sqlite3
from datetime import datetime
import json
import logging
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.database import db_service

logger = logging.getLogger('models.attack')


class Attack:
    """攻击记录模型类"""
    
    def __init__(self, attack_id=None, target_id=None, attack_type=None, attack_name=None, status='pending', result=None, start_time=None, end_time=None, created_at=None):
        self.attack_id = attack_id
        self.target_id = target_id
        self.attack_type = attack_type
        self.attack_name = attack_name
        self.status = status
        self.result = result
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at
    
    @staticmethod
    def get_by_id(attack_id):
        """根据ID获取攻击记录"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attacks WHERE attack_id = ?", (attack_id,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return Attack(
                        attack_id=row['attack_id'],
                        target_id=row['target_id'],
                        attack_type=row['attack_type'],
                        attack_name=row['attack_name'],
                        status=row['status'],
                        result=row['result'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            logger.error(f"获取攻击记录失败: {e}")
        return None
    
    @staticmethod
    def list_all(limit=100, offset=0, status=None, attack_type=None):
        """获取攻击记录列表"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM attacks"
                params = []
                
                conditions = []
                if status:
                    conditions.append("status = ?")
                    params.append(status)
                if attack_type:
                    conditions.append("attack_type = ?")
                    params.append(attack_type)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                attacks = []
                for row in rows:
                    attacks.append(Attack(
                        attack_id=row['attack_id'],
                        target_id=row['target_id'],
                        attack_type=row['attack_type'],
                        attack_name=row['attack_name'],
                        status=row['status'],
                        result=row['result'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        created_at=row['created_at']
                    ))
                return attacks
        except Exception as e:
            logger.error(f"获取攻击记录列表失败: {e}")
        return []
    
    @staticmethod
    def count(status=None):
        """统计攻击记录数量"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status = ?", (status,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM attacks")
                
                count = cursor.fetchone()[0]
                conn.close()
                return count
        except Exception as e:
            logger.error(f"统计攻击记录数量失败: {e}")
        return 0
    
    @staticmethod
    def get_stats():
        """获取攻击统计"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                
                # 总数
                cursor.execute("SELECT COUNT(*) FROM attacks")
                total = cursor.fetchone()[0]
                
                # 按状态统计
                cursor.execute("SELECT status, COUNT(*) FROM attacks GROUP BY status")
                status_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 按类型统计
                cursor.execute("SELECT attack_type, COUNT(*) FROM attacks GROUP BY attack_type")
                type_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                conn.close()
                
                return {
                    'total': total,
                    'status_counts': status_counts,
                    'type_counts': type_counts
                }
        except Exception as e:
            logger.error(f"获取攻击统计失败: {e}")
        return {'total': 0, 'status_counts': {}, 'type_counts': {}}
    
    def save(self):
        """保存攻击记录"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                
                if self.attack_id:
                    # 更新现有记录
                    cursor.execute("""
                        UPDATE attacks SET 
                        target_id = ?, attack_type = ?, attack_name = ?, status = ?, result = ?, start_time = ?, end_time = ?
                        WHERE attack_id = ?
                    """, (self.target_id, self.attack_type, self.attack_name, self.status, self.result, self.start_time, self.end_time, self.attack_id))
                else:
                    # 创建新记录
                    cursor.execute("""
                        INSERT INTO attacks (target_id, attack_type, attack_name, status, result, start_time, end_time, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (self.target_id, self.attack_type, self.attack_name, self.status, self.result, self.start_time, self.end_time, datetime.now().isoformat()))
                    self.attack_id = cursor.lastrowid
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"保存攻击记录失败: {e}")
        return False
    
    def delete(self):
        """删除攻击记录"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attacks WHERE attack_id = ?", (self.attack_id,))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"删除攻击记录失败: {e}")
        return False
    
    def update_status(self, status, result=None):
        """更新状态"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                if result:
                    cursor.execute("""
                        UPDATE attacks SET status = ?, result = ?, end_time = ? WHERE attack_id = ?
                    """, (status, result, datetime.now().isoformat(), self.attack_id))
                else:
                    cursor.execute("""
                        UPDATE attacks SET status = ? WHERE attack_id = ?
                    """, (status, self.attack_id))
                conn.commit()
                conn.close()
                self.status = status
                return True
        except Exception as e:
            logger.error(f"更新攻击状态失败: {e}")
        return False
    
    @staticmethod
    def get_attack_types():
        """获取攻击类型列表 - 使用标准安全攻击类型"""
        try:
            # 返回标准的网络安全攻击类型，基于开源安全工具的常见分类
            attack_types = [
                {'type': 'SQL Injection', 'category': 'Web攻击', 'description': 'SQL注入攻击，利用输入验证漏洞执行恶意SQL语句'},
                {'type': 'XSS', 'category': 'Web攻击', 'description': '跨站脚本攻击，在网页中注入恶意脚本'},
                {'type': 'CSRF', 'category': 'Web攻击', 'description': '跨站请求伪造，诱使用户执行非预期操作'},
                {'type': 'Command Injection', 'category': '系统攻击', 'description': '命令注入攻击，执行任意系统命令'},
                {'type': 'Path Traversal', 'category': '系统攻击', 'description': '路径遍历攻击，访问受限文件和目录'},
                {'type': 'Port Scan', 'category': '信息收集', 'description': '端口扫描，探测开放端口和服务'},
                {'type': 'Brute Force', 'category': '认证攻击', 'description': '暴力破解，尝试大量用户名密码组合'},
                {'type': 'DDoS', 'category': '拒绝服务', 'description': '分布式拒绝服务攻击，耗尽目标资源'},
                {'type': 'Buffer Overflow', 'category': '系统攻击', 'description': '缓冲区溢出，覆盖内存区域执行恶意代码'},
                {'type': 'Phishing', 'category': '社会工程学', 'description': '钓鱼攻击，诱骗用户提供敏感信息'},
                {'type': 'Man-in-the-Middle', 'category': '网络攻击', 'description': '中间人攻击，拦截和篡改通信'},
                {'type': 'Privilege Escalation', 'category': '系统攻击', 'description': '权限提升，获得更高权限访问'},
                {'type': 'Zero-Day Exploit', 'category': '高级攻击', 'description': '零日漏洞利用，利用未公开漏洞'},
                {'type': 'Social Engineering', 'category': '社会工程学', 'description': '社会工程学攻击，利用心理操纵获取信息'},
                {'type': 'Malware', 'category': '恶意软件', 'description': '恶意软件传播，如病毒、木马、勒索软件'},
                {'type': 'Network Sniffing', 'category': '网络攻击', 'description': '网络嗅探，截获网络数据包'},
                {'type': 'Session Hijacking', 'category': '会话攻击', 'description': '会话劫持，窃取用户会话令牌'},
                {'type': 'Directory Traversal', 'category': '系统攻击', 'description': '目录遍历，访问受限目录结构'}
            ]
            return attack_types
        except Exception as e:
            logger.error(f"获取攻击类型失败: {e}")
            # 出错时返回默认类型
            return [
                {'type': 'SQL Injection', 'category': 'Web攻击', 'description': 'SQL注入攻击，利用输入验证漏洞执行恶意SQL语句'},
                {'type': 'XSS', 'category': 'Web攻击', 'description': '跨站脚本攻击，在网页中注入恶意脚本'},
                {'type': 'CSRF', 'category': 'Web攻击', 'description': '跨站请求伪造，诱使用户执行非预期操作'},
                {'type': 'Command Injection', 'category': '系统攻击', 'description': '命令注入攻击，执行任意系统命令'},
                {'type': 'Port Scan', 'category': '信息收集', 'description': '端口扫描，探测开放端口和服务'}
            ]
    
    def to_dict(self):
        """转换为字典"""
        return {
            'attack_id': self.attack_id,
            'target_id': self.target_id,
            'attack_type': self.attack_type,
            'attack_name': self.attack_name,
            'status': self.status,
            'result': self.result,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'created_at': self.created_at
        }
