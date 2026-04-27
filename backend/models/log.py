import pymysql
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import DB_CONFIG


class Log:
    def __init__(self, log_id: int = None, level: str = None, source: str = None, 
                 message: str = None, user_id: int = None, target_id: int = None,
                 created_at: datetime = None):
        self.log_id = log_id
        self.level = level  # info, warning, danger, success
        self.source = source  # system, attack, defense, docker, etc.
        self.message = message
        self.user_id = user_id
        self.target_id = target_id
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字�?""
        return {
            'log_id': self.log_id,
            'level': self.level,
            'source': self.source,
            'message': self.message,
            'user_id': self.user_id,
            'target_id': self.target_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Log':
        """从字典创建日志对�?""
        log = cls()
        log.log_id = data.get('log_id')
        log.level = data.get('level')
        log.source = data.get('source')
        log.message = data.get('message')
        log.user_id = data.get('user_id')
        log.target_id = data.get('target_id')
        log.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        return log
    
    @classmethod
    def create(cls, level: str, source: str, message: str, user_id: int = None, 
               target_id: int = None) -> Optional['Log']:
        """创建新日�?""
        log = cls(level=level, source=source, message=message, user_id=user_id, target_id=target_id)
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO logs (level, source, message, user_id, target_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    log.level,
                    log.source,
                    log.message,
                    log.user_id,
                    log.target_id,
                    log.created_at
                ))
                connection.commit()
                log.log_id = cursor.lastrowid
                return log
        except Exception as e:
            print(f"Error creating log: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def list_all(cls, limit: int = 100, offset: int = 0, level: str = None, 
                 source: str = None, user_id: int = None, target_id: int = None) -> List['Log']:
        """获取日志列表"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM logs WHERE 1=1"
                params = []
                
                if level:
                    sql += " AND level = %s"
                    params.append(level)
                
                if source:
                    sql += " AND source = %s"
                    params.append(source)
                
                if user_id:
                    sql += " AND user_id = %s"
                    params.append(user_id)
                
                if target_id:
                    sql += " AND target_id = %s"
                    params.append(target_id)
                
                sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                
                logs = []
                for result in results:
                    columns = [desc[0] for desc in cursor.description]
                    log_data = dict(zip(columns, result))
                    logs.append(cls.from_dict(log_data))
                return logs
        except Exception as e:
            print(f"Error listing logs: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return []
    
    @classmethod
    def get_by_id(cls, log_id: int) -> Optional['Log']:
        """通过ID获取日志"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM logs WHERE log_id = %s"
                cursor.execute(sql, (log_id,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    log_data = dict(zip(columns, result))
                    return cls.from_dict(log_data)
        except Exception as e:
            print(f"Error getting log by ID: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def get_attack_logs(cls, limit: int = 50) -> List['Log']:
        """获取攻击日志"""
        return cls.list_all(limit=limit, source='attack')
    
    @classmethod
    def get_defense_logs(cls, limit: int = 50) -> List['Log']:
        """获取防御日志"""
        return cls.list_all(limit=limit, source='defense')
    
    @classmethod
    def get_system_logs(cls, limit: int = 50) -> List['Log']:
        """获取系统日志"""
        return cls.list_all(limit=limit, source='system')
    
    @classmethod
    def get_docker_logs(cls, limit: int = 50) -> List['Log']:
        """获取Docker日志"""
        return cls.list_all(limit=limit, source='docker')
    
    @classmethod
    def clear_logs(cls, older_than_days: int = None):
        """清理日志"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                if older_than_days:
                    sql = "DELETE FROM logs WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)"
                    cursor.execute(sql, (older_than_days,))
                else:
                    sql = "DELETE FROM logs"
                    cursor.execute(sql)
                connection.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"Error clearing logs: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return 0
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """获取日志统计"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 总日志数
                cursor.execute("SELECT COUNT(*) as total FROM logs")
                total = cursor.fetchone()[0]
                
                # 各级别日志数
                cursor.execute("SELECT level, COUNT(*) as count FROM logs GROUP BY level")
                level_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 各来源日志数
                cursor.execute("SELECT source, COUNT(*) as count FROM logs GROUP BY source")
                source_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 今日日志�?
                cursor.execute("SELECT COUNT(*) as today FROM logs WHERE DATE(created_at) = CURDATE()")
                today = cursor.fetchone()[0]
                
                return {
                    'total': total,
                    'level_counts': level_counts,
                    'source_counts': source_counts,
                    'today': today
                }
        except Exception as e:
            print(f"Error getting log stats: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return {}
    
    @classmethod
    def init_database(cls):
        """初始化日志表"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 创建日志�?
                sql = """
                CREATE TABLE IF NOT EXISTS logs (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    level ENUM('info', 'warning', 'danger', 'success') DEFAULT 'info',
                    source VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    user_id INT,
                    target_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
                    FOREIGN KEY (target_id) REFERENCES targets(target_id) ON DELETE SET NULL
                )
                """
                cursor.execute(sql)
                connection.commit()
        except Exception as e:
            print(f"Error initializing logs database: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
