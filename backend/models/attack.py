import asyncio
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
import pymysql
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import DB_CONFIG
from models.log import Log


class Attack:
    def __init__(self, attack_id: int = None, name: str = None, attack_type: str = None,
                 target: str = None, port: str = None, intensity: int = None,
                 status: str = 'pending', user_id: int = None, created_at: datetime = None,
                 completed_at: datetime = None):
        self.attack_id = attack_id
        self.name = name
        self.attack_type = attack_type
        self.target = target
        self.port = port
        self.intensity = intensity
        self.status = status  # pending, running, completed, failed
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.completed_at = completed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字�?""
        return {
            'attack_id': self.attack_id,
            'name': self.name,
            'attack_type': self.attack_type,
            'target': self.target,
            'port': self.port,
            'intensity': self.intensity,
            'status': self.status,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attack':
        """从字典创建攻击对�?""
        attack = cls()
        attack.attack_id = data.get('attack_id')
        attack.name = data.get('name')
        attack.attack_type = data.get('attack_type')
        attack.target = data.get('target')
        attack.port = data.get('port')
        attack.intensity = data.get('intensity')
        attack.status = data.get('status')
        attack.user_id = data.get('user_id')
        attack.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        attack.completed_at = datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        return attack
    
    @classmethod
    def get_by_id(cls, attack_id: int) -> Optional['Attack']:
        """通过ID获取攻击"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM attacks WHERE attack_id = %s"
                cursor.execute(sql, (attack_id,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    attack_data = dict(zip(columns, result))
                    return cls.from_dict(attack_data)
        except Exception as e:
            print(f"Error getting attack by ID: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def list_all(cls, user_id: int = None, limit: int = 50) -> List['Attack']:
        """获取所有攻击记�?""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                if user_id:
                    sql = "SELECT * FROM attacks WHERE user_id = %s ORDER BY created_at DESC LIMIT %s"
                    cursor.execute(sql, (user_id, limit))
                else:
                    sql = "SELECT * FROM attacks ORDER BY created_at DESC LIMIT %s"
                    cursor.execute(sql, (limit,))
                
                results = cursor.fetchall()
                attacks = []
                for result in results:
                    columns = [desc[0] for desc in cursor.description]
                    attack_data = dict(zip(columns, result))
                    attacks.append(cls.from_dict(attack_data))
                return attacks
        except Exception as e:
            print(f"Error listing attacks: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return []
    
    @classmethod
    def create(cls, name: str, attack_type: str, target: str, port: str, 
               intensity: int, user_id: int = None) -> Optional['Attack']:
        """创建新攻�?""
        attack = cls(name=name, attack_type=attack_type, target=target, 
                     port=port, intensity=intensity, user_id=user_id)
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO attacks (name, attack_type, target, port, intensity, status, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    attack.name,
                    attack.attack_type,
                    attack.target,
                    attack.port,
                    attack.intensity,
                    attack.status,
                    attack.user_id,
                    attack.created_at
                ))
                connection.commit()
                attack.attack_id = cursor.lastrowid
                return attack
        except Exception as e:
            print(f"Error creating attack: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    def update_status(self, status: str):
        """更新攻击状�?""
        self.status = status
        if status in ['completed', 'failed']:
            self.completed_at = datetime.now()
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "UPDATE attacks SET status = %s, completed_at = %s WHERE attack_id = %s"
                cursor.execute(sql, (status, self.completed_at, self.attack_id))
                connection.commit()
        except Exception as e:
            print(f"Error updating attack status: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
    
    def execute(self) -> Dict[str, Any]:
        """执行攻击"""
        self.update_status('running')
        
        # 记录攻击开始日�?
        Log.create('info', 'attack', f'开始执行攻�? {self.name} ({self.attack_type})', 
                   user_id=self.user_id)
        
        try:
            # 模拟攻击执行
            result = self._simulate_attack()
            
            # 记录攻击结果
            if result['success']:
                self.update_status('completed')
                Log.create('success', 'attack', 
                           f'攻击成功: {self.name} - {result["message"]}', 
                           user_id=self.user_id)
            else:
                self.update_status('failed')
                Log.create('danger', 'attack', 
                           f'攻击失败: {self.name} - {result["message"]}', 
                           user_id=self.user_id)
            
            return result
        except Exception as e:
            self.update_status('failed')
            Log.create('danger', 'attack', f'攻击异常: {self.name} - {str(e)}', 
                       user_id=self.user_id)
            return {'success': False, 'message': str(e)}
    
    def _simulate_attack(self) -> Dict[str, Any]:
        """模拟攻击执行"""
        attack_payloads = {
            'SQL注入': {
                'payload': "' OR '1'='1",
                'detection': "检测到SQL注入�?,
                'success_rate': 0.7
            },
            'XSS攻击': {
                'payload': '<script>alert(1)</script>',
                'detection': 'XSS漏洞确认',
                'success_rate': 0.6
            },
            '端口扫描': {
                'payload': 'TCP SYN扫描',
                'detection': '端口开放检�?,
                'success_rate': 0.9
            },
            '命令执行': {
                'payload': 'id; whoami',
                'detection': '命令执行漏洞',
                'success_rate': 0.5
            },
            'CSRF攻击': {
                'payload': '<img src="malicious.com">',
                'detection': 'CSRF漏洞检�?,
                'success_rate': 0.4
            }
        }
        
        payload_info = attack_payloads.get(self.attack_type, {
            'payload': '未知攻击类型',
            'detection': '未知检测方�?,
            'success_rate': 0.3
        })
        
        # 根据强度调整成功�?
        success_rate = payload_info['success_rate'] * (self.intensity / 10)
        
        # 模拟攻击结果
        if random.random() < success_rate:
            return {
                'success': True,
                'message': f"攻击成功: {payload_info['detection']}\n" +
                          f"执行Payload: {payload_info['payload']}\n" +
                          f"目标: {self.target}:{self.port}",
                'payload': payload_info['payload'],
                'detection': payload_info['detection']
            }
        else:
            return {
                'success': False,
                'message': f"攻击被阻�? {payload_info['detection']}\n" +
                          f"目标: {self.target}:{self.port}",
                'payload': payload_info['payload'],
                'detection': payload_info['detection']
            }
    
    @classmethod
    def get_attack_types(cls) -> List[Dict[str, Any]]:
        """获取支持的攻击类�?""
        return [
            {'value': 'SQL注入', 'label': 'SQL注入', 'category': 'Web漏洞'},
            {'value': 'XSS攻击', 'label': 'XSS跨站脚本', 'category': 'Web漏洞'},
            {'value': 'CSRF攻击', 'label': 'CSRF跨站请求伪�?, 'category': 'Web漏洞'},
            {'value': '命令执行', 'label': '命令执行', 'category': 'Web漏洞'},
            {'value': '端口扫描', 'label': '端口扫描', 'category': '网络攻击'},
            {'value': '暴力破解', 'label': '暴力破解', 'category': '网络攻击'},
            {'value': '权限提升', 'label': '权限提升', 'category': '系统攻击'},
            {'value': '容器逃�?, 'label': '容器逃�?, 'category': '系统攻击'}
        ]
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """获取攻击统计"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 总攻击数
                cursor.execute("SELECT COUNT(*) as total FROM attacks")
                total = cursor.fetchone()[0]
                
                # 成功/失败攻击�?
                cursor.execute("SELECT status, COUNT(*) as count FROM attacks GROUP BY status")
                status_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 各类型攻击数
                cursor.execute("SELECT attack_type, COUNT(*) as count FROM attacks GROUP BY attack_type")
                type_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 今日攻击�?
                cursor.execute("SELECT COUNT(*) as today FROM attacks WHERE DATE(created_at) = CURDATE()")
                today = cursor.fetchone()[0]
                
                return {
                    'total': total,
                    'success': status_counts.get('completed', 0),
                    'failed': status_counts.get('failed', 0),
                    'type_counts': type_counts,
                    'today': today
                }
        except Exception as e:
            print(f"Error getting attack stats: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return {}
    
    @classmethod
    def init_database(cls):
        """初始化攻击表"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 创建攻击�?
                sql = """
                CREATE TABLE IF NOT EXISTS attacks (
                    attack_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    attack_type VARCHAR(50) NOT NULL,
                    target VARCHAR(100) NOT NULL,
                    port VARCHAR(10) NOT NULL,
                    intensity INT DEFAULT 5,
                    status VARCHAR(20) DEFAULT 'pending',
                    user_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                )
                """
                cursor.execute(sql)
                connection.commit()
        except Exception as e:
            print(f"Error initializing attacks database: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
