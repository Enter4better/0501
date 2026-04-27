import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, Any
import pymysql
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import DB_CONFIG, SECURITY_CONFIG


class User:
    def __init__(self, user_id: int = None, username: str = None, email: str = None, 
                 password_hash: str = None, role: str = 'user', created_at: datetime = None,
                 last_login: datetime = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
    
    def set_password(self, password: str):
        """设置密码并生成哈希�?""
        salt = "cyber_range_salt"  # 在实际应用中应该使用随机�?
        self.password_hash = self._hash_password(password, salt)
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        salt = "cyber_range_salt"
        return self._hash_password(password, salt) == self.password_hash
    
    def _hash_password(self, password: str, salt: str) -> str:
        """密码哈希函数"""
        import hashlib
        sha256 = hashlib.sha256()
        sha256.update((password + salt).encode('utf-8'))
        return sha256.hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字�?""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对�?""
        user = cls()
        user.user_id = data.get('user_id')
        user.username = data.get('username')
        user.email = data.get('email')
        user.password_hash = data.get('password_hash')
        user.role = data.get('role', 'user')
        user.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        user.last_login = datetime.fromisoformat(data['last_login']) if data.get('last_login') else None
        return user
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """通过用户名获取用�?""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    user_data = dict(zip(columns, result))
                    return cls.from_dict(user_data)
        except Exception as e:
            print(f"Error getting user by username: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """通过ID获取用户"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    user_data = dict(zip(columns, result))
                    return cls.from_dict(user_data)
        except Exception as e:
            print(f"Error getting user by ID: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def create(cls, username: str, password: str, email: str = None, role: str = 'user') -> Optional['User']:
        """创建新用�?""
        user = cls(username=username, email=email, role=role)
        user.set_password(password)
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    user.username,
                    user.email,
                    user.password_hash,
                    user.role,
                    user.created_at
                ))
                connection.commit()
                user.user_id = cursor.lastrowid
                return user
        except Exception as e:
            print(f"Error creating user: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    def update_last_login(self):
        """更新最后登录时�?""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "UPDATE users SET last_login = %s WHERE user_id = %s"
                cursor.execute(sql, (datetime.now(), self.user_id))
                connection.commit()
        except Exception as e:
            print(f"Error updating last login: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
    
    @classmethod
    def init_database(cls):
        """初始化用户表"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 创建用户�?
                sql = """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100),
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
                """
                cursor.execute(sql)
                connection.commit()
                
                # 创建管理员账户（如果不存在）
                admin = cls.get_by_username('admin')
                if not admin:
                    cls.create('admin', 'admin123', 'admin@cyber-range.com', 'admin')
                    print("Admin user created")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
