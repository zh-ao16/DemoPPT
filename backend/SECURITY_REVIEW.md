# DemoPPT 数据库迁移安全审查报告

**审查时间:** 2026-05-04  
**审查范围:** /home/hg/.hermes/company/projects/DemoPPT/backend/  
**技术栈:** Python 3.11 / FastAPI / SQLite

---

## 一、SQL注入风险审查

### 1.1 参数化查询使用情况 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| user_auth.py | ✅ 安全 | 所有SQL使用`cursor.execute("...", (params,))`参数化查询 |
| subscription.py | ✅ 安全 | 所有SQL使用参数化查询 |
| api_auth.py | ✅ 安全 | 频次限制SQL使用参数化查询 |
| model_config.py | ✅ 安全 | 所有SQL使用参数化查询 |

### 1.2 高风险发现

**⚠️ 中风险: API Key验证不完善**

在 `main.py` 第269-270行:
```python
if not api_key or len(api_key) < 10 or api_key in ("sk-xxxx", "sk-***", ""):
    print(f"用户API Key无效，跳过: {api_key}")
```

- 简单字符串检测可被绕过
- 建议使用正则表达式验证格式

---

## 二、认证/授权缺陷审查

### 2.1 Token机制 ✅ 基本安全

**位置:** user_auth.py

- ✅ Token使用`secrets.token_urlsafe(32)`生成，符合安全标准
- ✅ Token有效期30天（TOKEN_EXPIRE_DAYS=30）
- ✅ 密码使用双重SHA256+盐哈希

### 2.2 鉴权装饰器分析

**位置:** api_auth.py

| 功能 | 状态 | 说明 |
|------|------|------|
| @require_auth | ✅ | 登录验证装饰器存在 |
| @require_subscription | ✅ | 订阅验证装饰器存在 |
| 公开接口白名单 | ✅ | 包含`/docs`, `/openapi.json`, `/redoc` |
| 频次限制 | ✅ | 已实现，基于IP和用户ID |

### 2.3 高风险发现

**🔴 高风险: 路径遍历漏洞**

在 `main.py` 第2380-2387行:
```python
@app.get("/api/download/{filename}")
async def download(filename: str):
    """下载PPTX"""
    filepath = OUTPUT_DIR / filename
    return FileResponse(str(filepath), ...)
```

**问题:**
- 用户可控制`filename`参数
- 未验证`filename`是否包含路径遍历字符（如`../`）
- 可能导致任意文件下载

**建议修复:**
```python
@app.get("/api/download/{filename}")
async def download(filename: str):
    # 验证文件名只包含安全字符
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(...)
```

---

## 三、数据加密问题审查

### 3.1 密码加密 ✅ 基本安全

**位置:** user_auth.py 第68-74行

```python
def hash_password(password: str, salt: str = "") -> str:
    if not salt:
        salt = secrets.token_hex(16)
    hash1 = hashlib.sha256((password + salt).encode()).hexdigest()
    hash2 = hashlib.sha256((hash1 + salt).encode()).hexdigest()
    return f"{salt}${hash2}"
```

- ✅ 使用SHA256双重哈希
- ✅ 使用随机盐

**改进建议:** 使用bcrypt或argon2替代SHA256

### 3.2 API Key加密 ⚠️ 弱加密

**位置:** model_config.py 第56-69行

```python
def simple_encrypt(key: str) -> str:
    """简单加密（实际项目用更安全的方式）"""
    import base64
    return base64.b64encode(key.encode()).decode()
```

**🔴 高风险:**
- Base64不是真正的加密，任何人都能解码
- 注释明确说明"实际项目用更安全的方式"
- 存储的是用户敏感API密钥

**建议:** 使用Fernet对称加密或AWS KMS等云密钥管理服务

---

## 四、敏感信息泄露审查

### 4.1 短信验证码泄露 ⚠️

**位置:** user_auth.py 第306行

```python
return {"success": True, "message": f"验证码已发送", "code": code}  # 调试用，生产环境删除code字段
```

**🔴 高风险:**
- 验证码在响应中返回
- 注释说"调试用，生产环境删除"，但代码仍在生产环境执行
- 攻击者可截获验证码

### 4.2 错误信息泄露 ⚠️

**位置:** 多处

```python
# user_auth.py 第195行
return {"success": False, "error": "手机号或密码错误"}
```

**说明:**
- 登录失败统一返回"手机号或密码错误"，不区分具体是哪个字段错误 ✅ 良好
- 但某些调试信息可能泄露系统内部状态

### 4.3 脱敏展示 ⚠️ 部分实现

**位置:** model_config.py 第114行

```python
r["api_key"] = simple_decrypt(r["api_key"])[:8] + "****"  # 只显示前8位
```

- ✅ API Key在列表展示时脱敏
- ✅ 但解密函数`simple_decrypt`可被调用还原完整Key

---

## 五、其他安全问题

### 5.1 CORS配置 ⚠️ 中风险

**位置:** main.py 第24行

```python
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
```

- 默认允许localhost开发环境
- 生产环境需明确配置CORS来源
- 建议添加CORS中间件严格校验

### 5.2 数据库文件权限 ⚠️

- users.db, subscription.db 等数据库文件权限为 `-rw-r--r--`
- 建议限制为 `600` 仅所有者可读写

### 5.3 缺少速率限制详情页 ⚠️

**位置:** api_auth.py

```python
RATE_LIMIT_REQUESTS = 60  # 每分钟最多请求次数
RATE_LIMIT_WINDOW = 60
```

- 60次/分钟对某些API可能过于宽松
- 建议对敏感操作（登录、支付）使用更严格限制

---

## 六、安全建议优先级

### 🔴 立即修复

1. **删除短信验证码返回** - user_auth.py 第306行删除`code`字段
2. **修复路径遍历漏洞** - main.py download端点增加文件名校验
3. **替换Base64加密** - model_config.py使用真正的加密库

### 🟡 近期修复

4. 升级密码哈希为bcrypt/argon2
5. 配置生产环境CORS白名单
6. 数据库文件权限设置为600

### 🟢 长期改进

7. 添加完整的日志审计系统
8. 实现IP黑名单机制
9. 添加双因素认证支持

---

## 七、总结

| 类别 | 发现数 | 高风险 | 中风险 | 低风险 |
|------|--------|--------|--------|--------|
| SQL注入 | 0 | 0 | 0 | 0 |
| 认证/授权 | 2 | 1 | 1 | 0 |
| 数据加密 | 2 | 1 | 1 | 0 |
| 敏感信息泄露 | 2 | 1 | 1 | 0 |
| **总计** | **6** | **3** | **3** | **0** |

**总体评价:** 代码整体质量较好，SQL注入防护到位，但存在3个高风险安全问题需要立即修复。

---

*报告生成时间: 2026-05-04*
