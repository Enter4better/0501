#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库内容的脚本
"""
import sqlite3
import os
from pathlib import Path

def check_database():
    # 连接到数据库
    db_path = Path('backend/data/ai_security_range.db')
    print(f'数据库文件存在: {db_path.exists()}')
    if db_path.exists():
        print(f'数据库文件大小: {db_path.stat().st_size} 字节')
    else:
        print('数据库文件不存在')
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 列出所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('\n数据库中的表:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # 检查用户表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        user_table_exists = cursor.fetchone() is not None
        print(f'\n用户表存在: {user_table_exists}')
        
        if user_table_exists:
            # 获取用户表结构
            cursor.execute('PRAGMA table_info(users);')
            columns = cursor.fetchall()
            print('\n用户表结构:')
            for col in columns:
                print(f'  {col[1]} ({col[2]}) - {"NOT NULL" if col[3] else "NULL"}, Default: {col[4]}')
            
            # 查询用户
            cursor.execute('SELECT COUNT(*) as count FROM users')
            count = cursor.fetchone()['count']
            print(f'\n用户表记录数: {count}')
            
            if count > 0:
                cursor.execute('SELECT * FROM users')
                users = cursor.fetchall()
                print('\n用户表内容:')
                for user in users:
                    print(f'  ID: {user["user_id"]}, Username: {user["username"]}, Email: {user["email"]}, Role: {user["role"]}, Created: {user["created_at"]}')
            else:
                print('\n用户表为空')
        else:
            print('\n用户表不存在')
        
        # 检查其他重要表
        important_tables = ['targets', 'attacks', 'defenses', 'logs']
        print('\n其他重要表状态:')
        for table in important_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
                count = cursor.fetchone()['count']
                print(f'  {table}: 存在, {count} 条记录')
            else:
                print(f'  {table}: 不存在')
        
        conn.close()
    except Exception as e:
        print(f'\n数据库连接错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_database()