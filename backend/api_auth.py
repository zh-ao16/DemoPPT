#!/usr/bin/env python3
"""
DemoPPT API鉴权中间件 v1.0
包含：Token验证、频次限制、权限检查装饰器
"""
from functools import wraps
from fastapi import Request, HTTPException
from typing import Callable, Optional
import time
import sqlite3
from pathlib import Path

# 频次限制配置
RATE_LIMIT_REQUESTS = 60  # 每分钟最多请求次数
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）
RATE_LIMIT_DB = Path(__file__).parent / "rate_limit.db"


def get_rate_limit_db():
    """获取频次限制数据库"""
    conn = sqlite3.connect(RATE_LIMIT_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_rate_limit_db():
    """初始化频次限制数据库"""
    conn = get_rate_limit_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 0,
            ip_address VARCHAR(50) DEFAULT '',
            endpoint VARCHAR(100) DEFAULT '',
            request_count INTEGER DEFAULT 0,
            window_start INTEGER NOT NULL,
            UNIQUE(user_id, ip_address, endpoint)
        )
    """)
    conn.commit()
    conn.close()


def check_rate_limit(user_id: int, ip_address: str, endpoint: str) -> tuple:
    """
    检查频次限制
    返回: (allowed: bool, remaining: int, reset_in: int)
    """
    now = int(time.time())
    window_start = now - RATE_LIMIT_WINDOW
    
    conn = get_rate_limit_db()
    cursor = conn.cursor()
    
    # 清理过期记录
    cursor.execute("DELETE FROM rate_limits WHERE window_start < ?", (window_start,))
    
    # 获取当前计数
    cursor.execute("""
        SELECT request_count, window_start FROM rate_limits
        WHERE user_id = ? AND ip_address = ? AND endpoint = ?
    """, (user_id, ip_address, endpoint))
    row = cursor.fetchone()
    
    if not row:
        # 新记录
        cursor.execute("""
            INSERT INTO rate_limits (user_id, ip_address, endpoint, request_count, window_start)
            VALUES (?, ?, ?, 1, ?)
        """, (user_id, ip_address, endpoint, now))
        conn.commit()
        conn.close()
        return True, RATE_LIMIT_REQUESTS - 1, RATE_LIMIT_WINDOW
    
    count = row["request_count"]
    ws = row["window_start"]
    
    if count >= RATE_LIMIT_REQUESTS:
        # 超过限制
        reset_in = (ws + RATE_LIMIT_WINDOW) - now
        conn.close()
        return False, 0, max(0, reset_in)
    
    # 更新计数
    cursor.execute("""
        UPDATE rate_limits SET request_count = request_count + 1
        WHERE user_id = ? AND ip_address = ? AND endpoint = ?
    """, (user_id, ip_address, endpoint))
    conn.commit()
    conn.close()
    
    remaining = RATE_LIMIT_REQUESTS - count - 1
    reset_in = (ws + RATE_LIMIT_WINDOW) - now
    
    return True, remaining, max(0, reset_in)


def get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


class AuthMiddleware:
    """API鉴权中间件"""
    
    # 不需要鉴权的接口（白名单）
    PUBLIC_ENDPOINTS = [
        "/",
        "/health",
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/send_sms",
        "/api/auth/verify_sms",
        "/api/plans",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    # 需要订阅的接口
    SUBSCRIPTION_REQUIRED = [
        "/api/generate_content",
        "/api/preview_content",
        "/api/digital_human",
    ]
    
    def __init__(self):
        init_rate_limit_db()
    
    def is_public(self, path: str) -> bool:
        """检查是否是公开接口"""
        for pattern in self.PUBLIC_ENDPOINTS:
            if path.startswith(pattern):
                return True
        return False
    
    def needs_subscription(self, path: str) -> bool:
        """检查是否需要订阅"""
        for pattern in self.SUBSCRIPTION_REQUIRED:
            if path.startswith(pattern):
                return True
        return False


auth_middleware = AuthMiddleware()


def require_auth(func: Callable) -> Callable:
    """
    登录验证装饰器
    用法: @require_auth
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # 检查公开接口
        if auth_middleware.is_public(request.url.path):
            return await func(request, *args, **kwargs)
        
        # 获取Token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="请先登录")
        
        token = auth_header[7:]
        
        # 验证Token
        from user_auth import verify_token
        user = verify_token(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Token无效或已过期")
        
        # 频次限制检查
        ip = get_client_ip(request)
        endpoint = request.url.path.split("/")[-1] or "index"
        allowed, remaining, reset_in = check_rate_limit(
            user["user_id"], ip, endpoint
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，请{reset_in}秒后重试"
            )
        
        # 将用户信息注入request state
        request.state.user = user
        request.state.user_id = user["user_id"]
        request.state.remaining_requests = remaining
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_subscription(func: Callable) -> Callable:
    """
    订阅验证装饰器（自动包含登录验证）
    用法: @require_subscription
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # 先验证登录
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="请先登录")
        
        token = auth_header[7:]
        
        from user_auth import verify_token
        user = verify_token(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Token无效或已过期")
        
        # 检查订阅
        from subscription import check_user_access
        access = check_user_access(user["user_id"])
        
        if not access["has_access"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "需要订阅才能使用此功能",
                    "plans": access["plans"],
                    "subscription": access["subscription"]
                }
            )
        
        # 注入用户和订阅信息
        request.state.user = user
        request.state.user_id = user["user_id"]
        request.state.subscription = access["subscription"]
        request.state.features = access.get("features", [])
        
        return await func(request, *args, **kwargs)
    
    return wrapper


# 初始化频次限制数据库
init_rate_limit_db()


if __name__ == "__main__":
    # 测试
    print("=== 频次限制测试 ===")
    allowed, remaining, reset_in = check_rate_limit(1, "127.0.0.1", "generate")
    print(f"请求1: allowed={allowed}, remaining={remaining}, reset_in={reset_in}")
    
    for i in range(2, 5):
        allowed, remaining, reset_in = check_rate_limit(1, "127.0.0.1", "generate")
        print(f"请求{i}: allowed={allowed}, remaining={remaining}, reset_in={reset_in}")
