import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import DB_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self) -> bool:
        """连接数据�?""
        try:
            self.connection = pymysql.connect(**DB_CONFIG)
            logger.info("数据库连接成�?)
            return True
        except Exception as e:
            logger.error(f"数据库连接失�? {e}")
            return False
    
    def disconnect(self):
        """断开数据库连�?""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已断开")
    
    def execute_query(self, query: str, params: tuple = None, fetch_all: bool = True) -> List[Dict[str, Any]]:
        """执行查询"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch_all:
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in results]
                else:
                    result = cursor.fetchone()
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result)) if result else None
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            if self.connection:
                self.connection.rollback()
            return 0
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """批量执行"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"批量执行失败: {e}")
            if self.connection:
                self.connection.rollback()
            return 0
    
    def init_database(self):
        """初始化数据库�?""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # 创建用户�?
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100),
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
                """)
                
                # 创建靶场�?
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS targets (
                    target_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    image VARCHAR(200) NOT NULL,
                    container_id VARCHAR(64),
                    port_mapping VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'created',
                    user_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                )
                """)
                
                # 创建日志�?
                cursor.execute("""
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
                """)
                
                # 创建攻击�?
                cursor.execute("""
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
                """)
                
                # 创建防御�?
                cursor.execute("""
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
                """)
                
                self.connection.commit()
                logger.info("数据库表初始化成�?)
                
                # 创建默认管理员用�?
                self._create_default_admin()
                
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            raise
    
    def _create_default_admin(self):
        """创建默认管理员用�?""
        try:
            # 检查是否已存在管理员用�?
            admin_user = self.execute_query(
                "SELECT * FROM users WHERE username = 'admin'",
                fetch_all=False
            )
            
            if not admin_user:
                # 创建管理员用�?
                import hashlib
                password = "admin123"
                salt = "cyber_range_salt"
                password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
                
                self.execute_update(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    ('admin', 'admin@cyber-range.com', password_hash, 'admin')
                )
                logger.info("默认管理员用户创建成�?)
        except Exception as e:
            logger.error(f"创建默认管理员用户失�? {e}")
    
    def get_connection(self):
        """获取数据库连�?""
        if not self.connection:
            self.connect()
        return self.connection
    
    def test_connection(self) -> bool:
        """测试数据库连�?""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失�? {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据�?""
        try:
            import subprocess
            
            # 构建mysqldump命令
            cmd = [
                'mysqldump',
                f'-h{DB_CONFIG["host"]}',
                f'-u{DB_CONFIG["user"]}',
                f'-p{DB_CONFIG["password"]}',
                DB_CONFIG["database"],
                '--routines',
                '--triggers'
            ]
            
            with open(backup_path, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            logger.info(f"数据库备份成�? {backup_path}")
            return True
        except Exception as e:
            logger.error(f"数据库备份失�? {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """恢复数据�?""
        try:
            import subprocess
            
            # 构建mysql命令
            cmd = [
                'mysql',
                f'-h{DB_CONFIG["host"]}',
                f'-u{DB_CONFIG["user"]}',
                f'-p{DB_CONFIG["password"]}',
                DB_CONFIG["database"]
            ]
            
            with open(backup_path, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True)
            
            logger.info(f"数据库恢复成�? {backup_path}")
            return True
        except Exception as e:
            logger.error(f"数据库恢复失�? {e}")
            return False


# 全局数据库服务实�?
db_service = DatabaseService()
