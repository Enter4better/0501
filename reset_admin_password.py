#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重置admin用户密码的脚本
"""

import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

def reset_admin_password():
    """重置admin用户密码为 admin123"""
    try:
        # 连接到数据库
        db_path = Path('backend/data/ai_security_range.db')
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 生成新的密码哈希
        new_password = 'admin123'
        hashed_password = generate_password_hash(new_password)
        
        # 更新admin用户的密码
        cursor.execute("""
            UPDATE users 
            SET password = ? 
            WHERE username = 'admin'
        """, (hashed_password,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"[SUCCESS] Admin用户密码已重置为: {new_password}")
            print(f"新密码哈希: {hashed_password}")
        else:
            print("[ERROR] 未找到admin用户")
        
        # 验证更新结果
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        user = cursor.fetchone()
        if user:
            print(f"\n验证用户信息:")
            print(f"  ID: {user['user_id']}")
            print(f"  Username: {user['username']}")
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
        
        conn.close()
        print("\n[INFO] 现在您可以使用以下凭据登录:")
        print("   用户名: admin")
        print("   密码: admin123")
        
    except Exception as e:
        print(f"[ERROR] 重置密码失败: {e}")

if __name__ == "__main__":
    reset_admin_password()