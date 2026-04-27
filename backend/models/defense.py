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


class Defense:
    def __init__(self, defense_id: int = None, name: str = None, defense_type: str = None,
                 description: str = None, enabled: bool = True, coverage: float = 0.0,
                 user_id: int = None, created_at: datetime = None, updated_at: datetime = None):
        self.defense_id = defense_id
        self.name = name
        self.defense_type = defense_type
        self.description = description
        self.enabled = enabled
        self.coverage = coverage
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字�?""
        return {
            'defense_id': self.defense_id,
            'name': self.name,
            'defense_type': self.defense_type,
            'description': self.description,
            'enabled': self.enabled,
            'coverage': self.coverage,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Defense':
        """从字典创建防御对�?""
        defense = cls()
        defense.defense_id = data.get('defense_id')
        defense.name = data.get('name')
        defense.defense_type = data.get('defense_type')
        defense.description = data.get('description')
        defense.enabled = data.get('enabled', True)
        defense.coverage = data.get('coverage', 0.0)
        defense.user_id = data.get('user_id')
        defense.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        defense.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        return defense
    
    @classmethod
    def get_by_id(cls, defense_id: int) -> Optional['Defense']:
        """通过ID获取防御规则"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM defenses WHERE defense_id = %s"
                cursor.execute(sql, (defense_id,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    defense_data = dict(zip(columns, result))
                    return cls.from_dict(defense_data)
        except Exception as e:
            print(f"Error getting defense by ID: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def list_all(cls, user_id: int = None) -> List['Defense']:
        """获取所有防御规�?""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                if user_id:
                    sql = "SELECT * FROM defenses WHERE user_id = %s ORDER BY created_at DESC"
                    cursor.execute(sql, (user_id,))
                else:
                    sql = "SELECT * FROM defenses ORDER BY created_at DESC"
                    cursor.execute(sql)
                
                results = cursor.fetchall()
                defenses = []
                for result in results:
                    columns = [desc[0] for desc in cursor.description]
                    defense_data = dict(zip(columns, result))
                    defenses.append(cls.from_dict(defense_data))
                return defenses
        except Exception as e:
            print(f"Error listing defenses: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return []
    
    @classmethod
    def create(cls, name: str, defense_type: str, description: str = None, 
               enabled: bool = True, coverage: float = 0.0, user_id: int = None) -> Optional['Defense']:
        """创建新防御规�?""
        defense = cls(name=name, defense_type=defense_type, description=description,
                      enabled=enabled, coverage=coverage, user_id=user_id)
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO defenses (name, defense_type, description, enabled, coverage, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    defense.name,
                    defense.defense_type,
                    defense.description,
                    defense.enabled,
                    defense.coverage,
                    defense.user_id,
                    defense.created_at,
                    defense.updated_at
                ))
                connection.commit()
                defense.defense_id = cursor.lastrowid
                return defense
        except Exception as e:
            print(f"Error creating defense: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    def update(self, name: str = None, defense_type: str = None, description: str = None,
               enabled: bool = None, coverage: float = None) -> bool:
        """更新防御规则"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 构建更新语句
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                    self.name = name
                
                if defense_type is not None:
                    updates.append("defense_type = %s")
                    params.append(defense_type)
                    self.defense_type = defense_type
                
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                    self.description = description
                
                if enabled is not None:
                    updates.append("enabled = %s")
                    params.append(enabled)
                    self.enabled = enabled
                
                if coverage is not None:
                    updates.append("coverage = %s")
                    params.append(coverage)
                    self.coverage = coverage
                
                if updates:
                    updates.append("updated_at = %s")
                    params.append(datetime.now())
                    
                    sql = f"UPDATE defenses SET {', '.join(updates)} WHERE defense_id = %s"
                    params.append(self.defense_id)
                    
                    cursor.execute(sql, params)
                    connection.commit()
                    return True
        except Exception as e:
            print(f"Error updating defense: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return False
    
    def toggle(self) -> bool:
        """切换防御规则状�?""
        return self.update(enabled=not self.enabled)
    
    def delete(self) -> bool:
        """删除防御规则"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "DELETE FROM defenses WHERE defense_id = %s"
                cursor.execute(sql, (self.defense_id,))
                connection.commit()
                return True
        except Exception as e:
            print(f"Error deleting defense: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return False
    
    @classmethod
    def get_default_defenses(cls) -> List['Defense']:
        """获取默认防御规则"""
        default_defenses = [
            cls(
                name='SQL注入防护',
                defense_type='WAF',
                description='检测并阻止SQL注入攻击',
                enabled=True,
                coverage=92.0
            ),
            cls(
                name='XSS攻击拦截',
                defense_type='WAF',
                description='检测并阻止跨站脚本攻击',
                enabled=True,
                coverage=88.0
            ),
            cls(
                name='端口扫描检�?,
                defense_type='IDS',
                description='检测端口扫描行�?,
                enabled=True,
                coverage=95.0
            ),
            cls(
                name='暴力破解阻断',
                defense_type='IPS',
                description='阻止暴力破解攻击',
                enabled=True,
                coverage=78.0
            ),
            cls(
                name='蜜罐诱饵节点',
                defense_type='蜜罐',
                description='诱捕攻击�?,
                enabled=False,
                coverage=0.0
            )
        ]
        
        # 保存到数据库
        saved_defenses = []
        for defense in default_defenses:
            saved = cls.create(defense.name, defense.defense_type, defense.description,
                             defense.enabled, defense.coverage)
            if saved:
                saved_defenses.append(saved)
        
        return saved_defenses
    
    def check_attack(self, attack_type: str, intensity: int) -> Dict[str, Any]:
        """检查攻击并返回防御结果"""
        if not self.enabled:
            return {
                'blocked': False,
                'message': f'防御规则 "{self.name}" 已禁�?,
                'defense_id': self.defense_id,
                'defense_name': self.name
            }
        
        # 根据防御类型和攻击类型计算拦截概�?
        block_probability = self._calculate_block_probability(attack_type, intensity)
        
        # 模拟防御结果
        is_blocked = random.random() < block_probability
        
        if is_blocked:
            message = f'成功拦截 {attack_type} 攻击'
            Log.create('success', 'defense', 
                      f'{self.name} 拦截攻击: {attack_type}', 
                      user_id=self.user_id)
        else:
            message = f'未能拦截 {attack_type} 攻击'
            Log.create('danger', 'defense', 
                      f'{self.name} 未能拦截攻击: {attack_type}', 
                      user_id=self.user_id)
        
        return {
            'blocked': is_blocked,
            'message': message,
            'defense_id': self.defense_id,
            'defense_name': self.name,
            'block_probability': block_probability
        }
    
    def _calculate_block_probability(self, attack_type: str, intensity: int) -> float:
        """计算拦截概率"""
        base_probabilities = {
            'SQL注入': 0.85,
            'XSS攻击': 0.80,
            'CSRF攻击': 0.75,
            '命令执行': 0.70,
            '端口扫描': 0.90,
            '暴力破解': 0.85,
            '权限提升': 0.60,
            '容器逃�?: 0.50
        }
        
        base_prob = base_probabilities.get(attack_type, 0.5)
        
        # 根据防御覆盖率调�?
        coverage_factor = self.coverage / 100.0
        
        # 根据攻击强度调整
        intensity_factor = max(0.1, 1.0 - (intensity - 5) * 0.1)
        
        # 计算最终概�?
        final_prob = base_prob * coverage_factor * intensity_factor
        return min(0.95, max(0.05, final_prob))
    
    @classmethod
    def get_defense_types(cls) -> List[Dict[str, Any]]:
        """获取支持的防御类�?""
        return [
            {'value': 'WAF', 'label': 'Web应用防火�?, 'description': '保护Web应用免受攻击'},
            {'value': 'IDS', 'label': '入侵检测系�?, 'description': '检测可疑活�?},
            {'value': 'IPS', 'label': '入侵防御系统', 'description': '主动阻止攻击'},
            {'value': '防火�?, 'label': '网络防火�?, 'description': '控制网络流量'},
            {'value': '蜜罐', 'label': '蜜罐系统', 'description': '诱捕攻击�?},
            {'value': '入侵检�?, 'label': '入侵检�?, 'description': '实时监控威胁'}
        ]
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """获取防御统计"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 总防御规则数
                cursor.execute("SELECT COUNT(*) as total FROM defenses")
                total = cursor.fetchone()[0]
                
                # 启用/禁用规则�?
                cursor.execute("SELECT enabled, COUNT(*) as count FROM defenses GROUP BY enabled")
                enabled_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 各类型规则数
                cursor.execute("SELECT defense_type, COUNT(*) as count FROM defenses GROUP BY defense_type")
                type_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 平均覆盖�?
                cursor.execute("SELECT AVG(coverage) as avg_coverage FROM defenses WHERE enabled = 1")
                avg_coverage = cursor.fetchone()[0] or 0
                
                return {
                    'total': total,
                    'enabled': enabled_counts.get(True, 0),
                    'disabled': enabled_counts.get(False, 0),
                    'type_counts': type_counts,
                    'avg_coverage': round(avg_coverage, 1)
                }
        except Exception as e:
            print(f"Error getting defense stats: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return {}
    
    @classmethod
    def init_database(cls):
        """初始化防御表"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 创建防御�?
                sql = """
                CREATE TABLE IF NOT EXISTS defenses (
                    defense_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    defense_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    enabled BOOLEAN DEFAULT TRUE,
                    coverage DECIMAL(5,2) DEFAULT 0.00,
                    user_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                )
                """
                cursor.execute(sql)
                connection.commit()
                
                # 创建默认防御规则
                if not cls.list_all():
                    cls.get_default_defenses()
                    print("Default defense rules created")
        except Exception as e:
            print(f"Error initializing defenses database: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
