#!/usr/bin/env python3
"""
DemoPPT 用户认证系统 v1.0
包含：注册、登录、Token验证、JWT Token管理
"""
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

# 数据库路径
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "users.db"

# Token配置
TOKEN_EXPIRE_DAYS = 30  # Token有效期（天）
TOKEN_TABLE = "auth_tokens"


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化用户数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone VARCHAR(20) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            nickname VARCHAR(50) DEFAULT '',
            avatar_url VARCHAR(500) DEFAULT '',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 1  -- 1=正常, 0=禁用
        )
    """)
    
    # Token表
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TOKEN_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token VARCHAR(128) UNIQUE NOT NULL,
            device_info VARCHAR(200) DEFAULT '',
            ip_address VARCHAR(50) DEFAULT '',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            expire_time DATETIME NOT NULL,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()


def hash_password(password: str, salt: str = "") -> str:
    """密码哈希（双重SHA256+盐）"""
    if not salt:
        salt = secrets.token_hex(16)
    hash1 = hashlib.sha256((password + salt).encode()).hexdigest()
    hash2 = hashlib.sha256((hash1 + salt).encode()).hexdigest()
    return f"{salt}${hash2}"


def verify_password(password: str, stored: str) -> bool:
    """验证密码"""
    try:
        salt, _ = stored.split("$")
        return hash_password(password, salt) == stored
    except:
        return False


def generate_token(user_id: int, device_info: str = "", ip_address: str = "") -> str:
    """生成Token"""
    token = secrets.token_urlsafe(32)
    expire_time = datetime.now() + timedelta(days=TOKEN_EXPIRE_DAYS)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {TOKEN_TABLE} (user_id, token, device_info, ip_address, expire_time)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, token, device_info, ip_address, expire_time))
    conn.commit()
    conn.close()
    
    return token


def verify_token(token: str) -> Optional[dict]:
    """验证Token，返回用户信息或None"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT t.user_id, t.expire_time, t.last_active,
               u.phone, u.nickname, u.avatar_url, u.status, u.create_time
        FROM {TOKEN_TABLE} t
        JOIN users u ON t.user_id = u.id
        WHERE t.token = ?
    """, (token,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # 检查是否过期
    expire_time = datetime.fromisoformat(row["expire_time"])
    if datetime.now() > expire_time:
        return None
    
    # 检查用户状态
    if row["status"] != 1:
        return None
    
    # 更新最后活跃时间
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {TOKEN_TABLE} SET last_active = CURRENT_TIMESTAMP WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    
    return {
        "user_id": row["user_id"],
        "phone": row["phone"],
        "nickname": row["nickname"],
        "avatar_url": row["avatar_url"],
        "status": row["status"],
        "create_time": row["create_time"],
        "expire_time": row["expire_time"]
    }


def register(phone: str, password: str, nickname: str = "") -> dict:
    """用户注册"""
    if not phone or len(phone) != 11:
        return {"success": False, "error": "手机号格式错误"}
    
    if len(password) < 6:
        return {"success": False, "error": "密码至少6位"}
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查手机号是否已注册
    cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "error": "手机号已注册"}
    
    # 创建用户
    password_hash = hash_password(password)
    cursor.execute("""
        INSERT INTO users (phone, password_hash, nickname)
        VALUES (?, ?, ?)
    """, (phone, password_hash, nickname or f"用户{phone[-4:]}"))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 生成Token
    token = generate_token(user_id)
    
    return {
        "success": True,
        "user_id": user_id,
        "token": token,
        "message": "注册成功"
    }


def login(phone: str, password: str, device_info: str = "", ip_address: str = "") -> dict:
    """用户登录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, nickname, avatar_url, status FROM users WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"success": False, "error": "手机号或密码错误"}
    
    if not verify_password(password, row["password_hash"]):
        return {"success": False, "error": "手机号或密码错误"}
    
    if row["status"] != 1:
        return {"success": False, "error": "账号已被禁用"}
    
    # 生成Token
    token = generate_token(row["id"], device_info, ip_address)
    
    return {
        "success": True,
        "user_id": row["id"],
        "token": token,
        "nickname": row["nickname"],
        "avatar_url": row["avatar_url"],
        "message": "登录成功"
    }


def logout(token: str) -> dict:
    """用户登出"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TOKEN_TABLE} WHERE token = ?", (token,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        return {"success": True, "message": "已退出登录"}
    return {"success": False, "error": "Token无效"}


def get_user_info(user_id: int) -> Optional[dict]:
    """获取用户信息"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, phone, nickname, avatar_url, create_time, status
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def update_user_info(user_id: int, nickname: str = None, avatar_url: str = None) -> dict:
    """更新用户信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    if nickname is not None:
        cursor.execute("UPDATE users SET nickname = ?, update_time = CURRENT_TIMESTAMP WHERE id = ?", (nickname, user_id))
    if avatar_url is not None:
        cursor.execute("UPDATE users SET avatar_url = ?, update_time = CURRENT_TIMESTAMP WHERE id = ?", (avatar_url, user_id))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "更新成功"}


def change_password(user_id: int, old_password: str, new_password: str) -> dict:
    """修改密码"""
    if len(new_password) < 6:
        return {"success": False, "error": "新密码至少6位"}
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"success": False, "error": "用户不存在"}
    
    if not verify_password(old_password, row["password_hash"]):
        conn.close()
        return {"success": False, "error": "原密码错误"}
    
    new_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = ?, update_time = CURRENT_TIMESTAMP WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "密码修改成功"}


def send_sms_code(phone: str, code: str) -> dict:
    """发送短信验证码（模拟版 - 实际需对接短信网关）"""
    # 实际项目中这里要对接创蓝/阿里云/腾讯云短信
    # 当前实现将验证码存入Redis或数据库用于验证
    conn = get_db()
    cursor = conn.cursor()
    
    # 存入验证码（有效期5分钟）
    expire_time = datetime.now() + timedelta(minutes=5)
    cursor.execute("""
        INSERT OR REPLACE INTO sms_codes (phone, code, expire_time)
        VALUES (?, ?, ?)
    """, (phone, code, expire_time))
    conn.commit()
    conn.close()
    
    # 模拟发送成功（实际项目要真实调用短信API）
    print(f"[SMS] 向 {phone} 发送验证码: {code}")
    return {"success": True, "message": f"验证码已发送", "code": code}  # 调试用，生产环境删除code字段


def verify_sms_code(phone: str, code: str) -> bool:
    """验证短信验证码"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT expire_time FROM sms_codes
        WHERE phone = ? AND code = ?
        ORDER BY id DESC LIMIT 1
    """, (phone, code))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
    
    expire_time = datetime.fromisoformat(row["expire_time"])
    if datetime.now() > expire_time:
        return False
    
    return True


# 初始化数据库
init_db()


if __name__ == "__main__":
    # 测试
    print("=== 用户认证测试 ===")
    
    # 测试注册
    r = register("13800138000", "password123", "测试用户")
    print(f"注册: {r}")
    
    # 测试登录
    r = login("13800138000", "password123")
    print(f"登录: {r}")
    
    if r["success"]:
        token = r["token"]
        
        # 验证Token
        user = verify_token(token)
        print(f"验证Token: {user}")
        
        # 获取用户信息
        info = get_user_info(user["user_id"])
        print(f"用户信息: {info}")
