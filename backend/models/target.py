# -*- coding: utf-8 -*-
"""
目标环境模型 - SQLite实现
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

logger = logging.getLogger('models.target')


class Target:
    """目标环境模型类"""
    
    def __init__(self, target_id=None, name=None, type='vm', ip=None, port=None, os=None, status='offline', config=None, created_at=None, updated_at=None):
        self.target_id = target_id
        self.name = name
        self.type = type
        self.ip = ip
        self.port = port
        self.os = os
        self.status = status
        self.config = config
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_by_id(target_id):
        """根据ID获取目标"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM targets WHERE target_id = ?", (target_id,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return Target(
                        target_id=row['target_id'],
                        name=row['name'],
                        type=row['type'],
                        ip=row['ip'],
                        port=row['port'],
                        os=row['os'],
                        status=row['status'],
                        config=row['config'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
        except Exception as e:
            logger.error(f"获取目标失败: {e}")
        return None
    
    @staticmethod
    def get_by_name(name):
        """根据名称获取目标"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM targets WHERE name = ?", (name,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return Target(
                        target_id=row['target_id'],
                        name=row['name'],
                        type=row['type'],
                        ip=row['ip'],
                        port=row['port'],
                        os=row['os'],
                        status=row['status'],
                        config=row['config'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
        except Exception as e:
            logger.error(f"获取目标失败: {e}")
        return None
    
    @staticmethod
    def list_all():
        """获取所有目标"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM targets ORDER BY created_at DESC")
                rows = cursor.fetchall()
                conn.close()
                
                targets = []
                for row in rows:
                    targets.append(Target(
                        target_id=row['target_id'],
                        name=row['name'],
                        type=row['type'],
                        ip=row['ip'],
                        port=row['port'],
                        os=row['os'],
                        status=row['status'],
                        config=row['config'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                return targets
        except Exception as e:
            logger.error(f"获取目标列表失败: {e}")
        return []
    
    @staticmethod
    def count():
        """统计目标数量"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM targets")
                count = cursor.fetchone()[0]
                conn.close()
                return count
        except Exception as e:
            logger.error(f"统计目标数量失败: {e}")
        return 0
    
    def save(self):
        """保存目标"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                
                if self.target_id:
                    # 更新现有目标
                    cursor.execute("""
                        UPDATE targets SET 
                        name = ?, type = ?, ip = ?, port = ?, os = ?, status = ?, config = ?, updated_at = ?
                        WHERE target_id = ?
                    """, (self.name, self.type, self.ip, self.port, self.os, self.status, self.config, datetime.now().isoformat(), self.target_id))
                else:
                    # 创建新目标
                    cursor.execute("""
                        INSERT INTO targets (name, type, ip, port, os, status, config, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (self.name, self.type, self.ip, self.port, self.os, self.status, self.config, datetime.now().isoformat(), datetime.now().isoformat()))
                    self.target_id = cursor.lastrowid
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"保存目标失败: {e}")
        return False
    
    def delete(self):
        """删除目标"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM targets WHERE target_id = ?", (self.target_id,))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"删除目标失败: {e}")
        return False
    
    def update_status(self, status):
        """更新状态"""
        try:
            conn = db_service.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE targets SET status = ?, updated_at = ? WHERE target_id = ?
                """, (status, datetime.now().isoformat(), self.target_id))
                conn.commit()
                conn.close()
                self.status = status
                return True
        except Exception as e:
            logger.error(f"更新目标状态失败: {e}")
        return False
    
    def to_dict(self):
        """转换为字典"""
        return {
            'target_id': self.target_id,
            'name': self.name,
            'type': self.type,
            'ip': self.ip,
            'port': self.port,
            'os': self.os,
            'status': self.status,
            'config': self.config,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }