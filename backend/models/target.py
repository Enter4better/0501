from datetime import datetime
from typing import Optional, List, Dict, Any
import pymysql
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import DB_CONFIG, DOCKER_CONFIG

# 尝试导入docker�?
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None


class Target:
    def __init__(self, target_id: int = None, name: str = None, image: str = None, 
                 container_id: str = None, port_mapping: str = None, status: str = 'created',
                 user_id: int = None, created_at: datetime = None, updated_at: datetime = None):
        self.target_id = target_id
        self.name = name
        self.image = image
        self.container_id = container_id
        self.port_mapping = port_mapping
        self.status = status
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字�?""
        return {
            'target_id': self.target_id,
            'name': self.name,
            'image': self.image,
            'container_id': self.container_id,
            'port_mapping': self.port_mapping,
            'status': self.status,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Target':
        """从字典创建靶场对�?""
        target = cls()
        target.target_id = data.get('target_id')
        target.name = data.get('name')
        target.image = data.get('image')
        target.container_id = data.get('container_id')
        target.port_mapping = data.get('port_mapping')
        target.status = data.get('status')
        target.user_id = data.get('user_id')
        target.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        target.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        return target
    
    @classmethod
    def get_by_id(cls, target_id: int) -> Optional['Target']:
        """通过ID获取靶场"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM targets WHERE target_id = %s"
                cursor.execute(sql, (target_id,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    target_data = dict(zip(columns, result))
                    return cls.from_dict(target_data)
        except Exception as e:
            print(f"Error getting target by ID: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Target']:
        """通过名称获取靶场"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT * FROM targets WHERE name = %s"
                cursor.execute(sql, (name,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    target_data = dict(zip(columns, result))
                    return cls.from_dict(target_data)
        except Exception as e:
            print(f"Error getting target by name: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    @classmethod
    def list_all(cls, user_id: int = None) -> List['Target']:
        """获取所有靶场列�?""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                if user_id:
                    sql = "SELECT * FROM targets WHERE user_id = %s ORDER BY created_at DESC"
                    cursor.execute(sql, (user_id,))
                else:
                    sql = "SELECT * FROM targets ORDER BY created_at DESC"
                    cursor.execute(sql)
                
                results = cursor.fetchall()
                targets = []
                for result in results:
                    columns = [desc[0] for desc in cursor.description]
                    target_data = dict(zip(columns, result))
                    targets.append(cls.from_dict(target_data))
                return targets
        except Exception as e:
            print(f"Error listing targets: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        return []
    
    @classmethod
    def create(cls, name: str, image: str, port_mapping: str, user_id: int = None) -> Optional['Target']:
        """创建新靶�?""
        target = cls(name=name, image=image, port_mapping=port_mapping, user_id=user_id)
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO targets (name, image, port_mapping, status, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    target.name,
                    target.image,
                    target.port_mapping,
                    target.status,
                    target.user_id,
                    target.created_at,
                    target.updated_at
                ))
                connection.commit()
                target.target_id = cursor.lastrowid
                return target
        except Exception as e:
            print(f"Error creating target: {e}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()
        return None
    
    def update_status(self, status: str):
        """更新靶场状�?""
        self.status = status
        self.updated_at = datetime.now()
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "UPDATE targets SET status = %s, updated_at = %s WHERE target_id = %s"
                cursor.execute(sql, (status, self.updated_at, self.target_id))
                connection.commit()
        except Exception as e:
            print(f"Error updating target status: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
    
    def delete(self):
        """删除靶场"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "DELETE FROM targets WHERE target_id = %s"
                cursor.execute(sql, (self.target_id,))
                connection.commit()
        except Exception as e:
            print(f"Error deleting target: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
    
    def start_container(self) -> bool:
        """启动Docker容器"""
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(self.container_id)
            container.start()
            self.update_status('running')
            return True
        except Exception as e:
            print(f"Error starting container: {e}")
            return False
    
    def stop_container(self) -> bool:
        """停止Docker容器"""
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(self.container_id)
            container.stop(timeout=10)
            self.update_status('stopped')
            return True
        except Exception as e:
            print(f"Error stopping container: {e}")
            return False
    
    def remove_container(self) -> bool:
        """删除Docker容器"""
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(self.container_id)
            container.remove(force=True)
            self.delete()
            return True
        except Exception as e:
            print(f"Error removing container: {e}")
            return False
    
    @classmethod
    def create_container(cls, name: str, image: str, port_mapping: str, user_id: int = None) -> Optional['Target']:
        """创建并启动Docker容器"""
        try:
            docker_client = docker.from_env()
            
            # 解析端口映射
            host_port, container_port = port_mapping.split(':')
            
            # 创建容器
            container = docker_client.containers.run(
                image,
                name=name,
                detach=True,
                ports={f'{container_port}/tcp': ('127.0.0.1', int(host_port))},
                remove=False
            )
            
            # 创建靶场记录
            target = cls.create(name, image, port_mapping, user_id)
            if target:
                target.container_id = container.id
                target.update_status('running')
                return target
        except Exception as e:
            print(f"Error creating container: {e}")
        return None
    
    @classmethod
    def init_database(cls):
        """初始化靶场表"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # 创建靶场�?
                sql = """
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
                """
                cursor.execute(sql)
                connection.commit()
        except Exception as e:
            print(f"Error initializing targets database: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
