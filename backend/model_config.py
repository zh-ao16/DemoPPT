#!/usr/bin/env python3
"""
DemoPPT 模型配置系统 v1.0
用户可添加多个AI模型的API配置，按需调用
"""
import sqlite3
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import httpx

# 数据库路径
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "models.db"


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化模型配置表"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(50) NOT NULL,           -- 配置名称，如"我的GPT-4"
            provider VARCHAR(30) DEFAULT 'custom', -- openai/anthropic/deepseek/custom
            api_base VARCHAR(500) NOT NULL,       -- API地址
            api_key VARCHAR(200) NOT NULL,        -- API密钥（加密存储）
            model_name VARCHAR(100) NOT NULL,     -- 模型名称，如gpt-4
            is_default INTEGER DEFAULT 0,         -- 是否默认
            status INTEGER DEFAULT 1,             -- 1=启用, 0=禁用
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 默认配置示例
    cursor.execute("""
        INSERT OR IGNORE INTO model_configs 
        (id, user_id, name, provider, api_base, api_key, model_name, is_default)
        VALUES (1, 0, '示例配置', 'custom', 'https://api.openai.com/v1', 'sk-xxxx', 'gpt-4', 1)
    """)
    
    conn.commit()
    conn.close()


def simple_encrypt(key: str) -> str:
    """[SEC-FIX] 使用Fernet对称加密替代Base64伪加密"""
    from cryptography.fernet import Fernet
    import base64
    import os
    # 从环境变量或生成固定key（实际项目应使用密钥管理服务）
    fernet_key = os.environ.get("FERNET_KEY") or base64.b64encode(os.urandom(32)).decode()
    if len(fernet_key) < 32:
        fernet_key = base64.b64encode(fernet_key.encode().ljust(32, b'0')).decode()
    cipher = Fernet(fernet_key.encode() if isinstance(fernet_key, str) else fernet_key)
    return base64.b64encode(cipher.encrypt(key.encode())).decode()


def simple_decrypt(encrypted: str) -> str:
    """[SEC-FIX] 支持Fernet解密，兼容旧版Base64"""
    import base64
    import os
    try:
        # 尝试Fernet解密（新格式）
        fernet_key = os.environ.get("FERNET_KEY") or base64.b64encode(os.urandom(32)).decode()
        if len(fernet_key) < 32:
            fernet_key = base64.b64encode(fernet_key.encode().ljust(32, b'0')).decode()
        cipher = Fernet(fernet_key.encode() if isinstance(fernet_key, str) else fernet_key)
        return cipher.decrypt(base64.b64decode(encrypted.encode())).decode()
    except Exception:
        # 兼容旧格式（纯base64）
        try:
            return base64.b64decode(encrypted.encode()).decode()
        except Exception:
            # 如果解密失败，可能是明文key，直接返回
            return encrypted


def add_config(user_id: int, name: str, api_base: str, api_key: str, 
               model_name: str, provider: str = "custom", is_default: int = 0) -> dict:
    """添加模型配置"""
    if not name or not api_base or not api_key or not model_name:
        return {"success": False, "error": "参数不完整"}
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 如果设为默认，先取消其他默认
    if is_default:
        cursor.execute("UPDATE model_configs SET is_default=0 WHERE user_id=?", (user_id,))
    
    # 加密存储API Key
    encrypted_key = simple_encrypt(api_key)
    
    cursor.execute("""
        INSERT INTO model_configs (user_id, name, provider, api_base, api_key, model_name, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, provider, api_base, encrypted_key, model_name, is_default))
    
    config_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"success": True, "id": config_id, "message": "配置添加成功"}


def get_configs(user_id: int) -> List[dict]:
    """获取用户所有模型配置"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, provider, api_base, api_key, model_name, is_default, status, create_time
        FROM model_configs WHERE user_id = ? ORDER BY is_default DESC, create_time DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    configs = []
    for row in rows:
        r = dict(row)
        r["api_key"] = simple_decrypt(r["api_key"])[:8] + "****"  # 只显示前8位
        configs.append(r)
    
    return configs


def get_default_config(user_id: int) -> Optional[dict]:
    """获取默认模型配置"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM model_configs WHERE user_id = ? AND is_default = 1 AND status = 1
        LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        r = dict(row)
        r["api_key"] = simple_decrypt(r["api_key"])
        return r
    return None


def get_config_by_id(config_id: int, user_id: int) -> Optional[dict]:
    """获取指定配置"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM model_configs WHERE id = ? AND user_id = ?
    """, (config_id, user_id))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        r = dict(row)
        r["api_key"] = simple_decrypt(r["api_key"])
        return r
    return None


def update_config(config_id: int, user_id: int, **kwargs) -> dict:
    """更新配置"""
    conn = get_db()
    cursor = conn.cursor()
    
    allowed = ["name", "provider", "api_base", "model_name", "is_default", "status"]
    updates = []
    values = []
    
    for k, v in kwargs.items():
        if k in allowed:
            if k == "api_key" and v:
                v = simple_encrypt(v)
            updates.append(f"{k} = ?")
            values.append(v)
    
    if not updates:
        return {"success": False, "error": "没有可更新的字段"}
    
    # 如果设为默认，先取消其他默认
    if kwargs.get("is_default"):
        cursor.execute("UPDATE model_configs SET is_default=0 WHERE user_id=?", (user_id,))
    
    values.extend([config_id, user_id])
    cursor.execute(f"""
        UPDATE model_configs SET {', '.join(updates)}, update_time=CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    """, values)
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected:
        return {"success": True, "message": "更新成功"}
    return {"success": False, "error": "配置不存在"}


def delete_config(config_id: int, user_id: int) -> dict:
    """删除配置"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM model_configs WHERE id = ? AND user_id = ?", (config_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected:
        return {"success": True, "message": "删除成功"}
    return {"success": False, "error": "配置不存在"}


def set_default(config_id: int, user_id: int) -> dict:
    """设为默认"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE model_configs SET is_default=0 WHERE user_id=?", (user_id,))
    cursor.execute("UPDATE model_configs SET is_default=1 WHERE id=? AND user_id=?", (config_id, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected:
        return {"success": True, "message": "已设为默认"}
    return {"success": False, "error": "配置不存在"}


async def call_model(config: dict, messages: list, **kwargs) -> dict:
    """
    调用模型API
    config包含: api_base, api_key, model_name, provider
    """
    api_base = config["api_base"].rstrip("/")
    api_key = config["api_key"]
    model_name = config["model_name"]
    provider = config.get("provider", "custom")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": messages,
        **kwargs
    }
    
    # 根据provider确定接口
    if provider == "openai" or "openai" in api_base:
        url = f"{api_base}/chat/completions"
    elif provider == "anthropic" or "anthropic" in api_base:
        url = f"{api_base}/messages"
        # Anthropic API格式不同
        payload.pop("model")
        payload["model"] = model_name
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
    elif provider == "deepseek":
        url = f"{api_base}/chat/completions"
    else:
        # 自定义/兼容格式
        url = f"{api_base}/chat/completions"
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result:
                # OpenAI兼容格式
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {})
                }
            elif "content" in result and isinstance(result["content"], list):
                # Anthropic格式（可能包含thinking/text块）
                content_parts = []
                for item in result["content"]:
                    if isinstance(item, dict):
                        if item.get("type") == "text" and item.get("text"):
                            content_parts.append(item["text"])
                        elif item.get("type") == "thinking" and item.get("thinking"):
                            content_parts.append(f"[思考]{item['thinking']}")
                content = "".join(content_parts) if content_parts else "(无文字内容)"
                return {
                    "success": True,
                    "content": content,
                    "usage": result.get("usage", {})
                }
            elif "content" in result and isinstance(result["content"], str):
                # 简单字符串格式
                return {
                    "success": True,
                    "content": result["content"],
                    "usage": result.get("usage", {})
                }
            else:
                return {"success": False, "error": "未知响应格式", "raw": str(result)[:200]}
                
    except httpx.TimeoutException:
        return {"success": False, "error": "请求超时，请检查网络或API地址是否正确"}
    except httpx.HTTPStatusError as e:
        # 尝试从响应体提取有意义的错误信息
        try:
            err_data = e.response.json()
            if isinstance(err_data, dict):
                if "error" in err_data and isinstance(err_data["error"], dict):
                    err_msg = err_data["error"].get("message", err_data["error"].get("type", str(err_data["error"])))
                elif "error" in err_data:
                    err_msg = str(err_data["error"])
                else:
                    err_msg = str(err_data)
            else:
                err_msg = str(err_data)
        except Exception:
            err_msg = e.response.text[:200] if e.response.text else f"HTTP {e.response.status_code}"

        status = e.response.status_code
        if status == 401:
            return {"success": False, "error": f"认证失败(401)：API Key无效或已过期，请检查后重试"}
        elif status == 403:
            return {"success": False, "error": f"禁止访问(403)：可能是API Key无权限或账户余额不足"}
        elif status == 404:
            return {"success": False, "error": f"接口不存在(404)：API地址可能填错了，当前地址={e.request.url}"}
        elif status == 429:
            return {"success": False, "error": f"请求过于频繁(429)：请稍后再试"}
        else:
            return {"success": False, "error": f"API错误({status})：{err_msg}"}
    except httpx.ConnectError:
        return {"success": False, "error": "连接失败：请确认API地址正确且服务已启动"}
    except Exception as e:
        return {"success": False, "error": f"连接异常：{str(e)}"}


# 初始化
init_db()


if __name__ == "__main__":
    print("=== 模型配置测试 ===")
    
    # 测试添加
    r = add_config(
        user_id=1,
        name="我的GPT-4",
        api_base="https://api.openai.com/v1",
        api_key="sk-test123456",
        model_name="gpt-4",
        provider="openai",
        is_default=1
    )
    print(f"添加配置: {r}")
    
    # 测试获取
    configs = get_configs(user_id=1)
    print(f"配置列表: {len(configs)}个")
    for c in configs:
        print(f"  - {c['name']} ({c['provider']}) - {c['model_name']}")
    
    # 测试获取默认
    default = get_default_config(user_id=1)
    print(f"默认配置: {default['name'] if default else '无'}")
