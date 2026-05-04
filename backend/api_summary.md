# DemoPPT v2.4 API文档摘要

**后端版本：** v2.3.0  
**框架：** FastAPI  
**生成时间：** 2026-05-04

---

## 一、API概览

### 1.1 服务信息

| 项目 | 值 |
|-----|-----|
| 标题 | DemoPPT API |
| 版本 | 2.3.0 |
| 基础路径 | `/` |
| 健康检查 | `GET /health` |

### 1.2 OpenAPI/Swagger文档

❌ **未发现** - 当前项目没有配置OpenAPI/Swagger文档

**建议：** 为改善开发体验，建议添加：
```python
# 在main.py中添加
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

app = FastAPI(title="DemoPPT API", version="2.3.0", docs_url=None, redoc_url=None)

@app.get("/docs", include_in_schema=False)
async def get_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="DemoPPT API")

@app.get("/redoc", include_in_schema=False)
async def get_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="DemoPPT API")
```

---

## 二、API端点清单

### 2.1 健康检查

| 方法 | 端点 | 功能 |
|-----|------|------|
| GET | `/health` | 服务健康检查 |
| GET | `/` | 根路径，返回服务信息 |

### 2.2 PPT生成

| 方法 | 端点 | 功能 |
|-----|------|------|
| POST | `/api/generate_outline` | 生成PPT大纲 |
| POST | `/api/preview_content` | 单页内容预览 |
| GET | `/api/progress/{session_id}` | SSE生成进度推送 |
| POST | `/api/generate_content` | 生成完整PPT内容 |
| GET | `/api/download/{filename}` | 下载生成的PPT |

### 2.3 模板与配色

| 方法 | 端点 | 功能 |
|-----|------|------|
| GET | `/api/templates` | 获取模板列表 |
| GET | `/api/color_palettes` | 获取预设配色方案 |
| POST | `/api/generate_palette` | AI生成配色方案 |
| POST | `/api/preview_palette` | 预览配色效果 |

### 2.4 行业与知识库

| 方法 | 端点 | 功能 |
|-----|------|------|
| GET | `/api/industries` | 获取行业列表 |
| GET | `/api/search_industry` | 搜索行业知识 |
| GET | `/api/industry_kb` | 获取行业知识库 |
| GET | `/api/kb/stats` | 知识库统计 |
| GET | `/api/kb/documents` | 获取文档列表 |
| POST | `/api/kb/documents` | 创建文档 |
| POST | `/api/kb/upload` | 上传文档 |
| DELETE | `/api/kb/documents/{doc_id}` | 删除文档 |
| GET | `/api/kb/search` | 搜索知识库 |
| GET | `/api/kb/context` | 获取上下文 |

### 2.5 文档转换

| 方法 | 端点 | 功能 |
|-----|------|------|
| POST | `/api/convert_document` | 文档转PPT |
| POST | `/api/upload_document` | 上传文档 |
| POST | `/api/import_document` | 导入外部文档 |

### 2.6 历史记录

| 方法 | 端点 | 功能 |
|-----|------|------|
| POST | `/api/history` | 创建历史记录 |
| GET | `/api/history` | 获取历史记录列表 |
| DELETE | `/api/history/{hist_id}` | 删除历史记录 |

### 2.7 认证

| 方法 | 端点 | 功能 |
|-----|------|------|
| GET | `/api/auth/me` | 获取当前用户信息 |
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/logout` | 用户登出 |
| POST | `/api/auth/send_sms` | 发送短信验证码 |
| POST | `/api/auth/verify_sms` | 验证短信验证码 |
| PUT | `/api/auth/nickname` | 修改昵称 |
| PUT | `/api/auth/password` | 修改密码 |

### 2.8 订阅与付费

| 方法 | 端点 | 功能 |
|-----|------|------|
| GET | `/api/plans` | 获取套餐列表 |
| GET | `/api/subscription` | 获取订阅信息 |
| POST | `/api/subscription/create` | 创建订阅 |
| POST | `/api/subscription/cancel` | 取消订阅 |
| GET | `/api/subscription/check` | 检查订阅状态 |
| GET | `/api/orders` | 获取订单列表 |

### 2.9 AI模型配置

| 方法 | 端点 | 功能 |
|-----|------|------|
| GET | `/api/set_model` | 设置默认AI模型 |
| GET | `/api/models` | 获取支持的模型列表 |
| GET | `/api/models/default` | 获取默认模型配置 |
| POST | `/api/models` | 创建自定义模型配置 |

### 2.10 高级功能

| 方法 | 端点 | 功能 |
|-----|------|------|
| POST | `/api/digital_human` | 数字人合成 |
| POST | `/api/polish_content` | 内容润色优化 |
| GET | `/api/search_image` | 搜索图片素材 |
| POST | `/api/export_video` | 导出视频 |
| POST | `/api/beautify` | 美化PPT |

---

## 三、请求/响应模型

### 3.1 OutlineRequest
```json
{
  "topic": "string",
  "requirements": "string (optional)",
  "industry": "string (default: general)",
  "model_config_id": "number (optional)"
}
```

### 3.2 ContentRequest
```json
{
  "topic": "string",
  "outline": [{"title": "string", "type": "string"}],
  "template": "string (default: academic)",
  "industry": "string (optional)",
  "speaker_notes": "boolean (optional)",
  "brand_name": "string (optional)",
  "brand_logo": "string (optional)",
  "brand_color": "string (optional)",
  "language": "string (default: zh)",
  "model_config_id": "number (optional)"
}
```

### 3.3 DocumentConvertRequest
```json
{
  "text": "string",
  "industry": "string (default: general)",
  "template": "string (default: business)",
  "model_config_id": "number (optional)"
}
```

---

## 四、AI模型支持

### 4.1 支持的模型

| 模型ID | 名称 | 厂商 | 支持函数调用 |
|-------|------|------|-------------|
| deepseek | DeepSeek | 深度求索 | ✅ |
| doubao | 豆包 | 字节跳动 | ❌ |
| zhipu | 智谱GLM | 智谱AI | ✅ |
| qwen | 通义千问 | 阿里云 | ✅ |
| wenxin | 文心一言 | 百度 | ✅ |
| hunyuan | 腾讯混元 | 腾讯云 | ❌ |
| spark | 讯飞星火 | 科大讯飞 | ❌ |
| minimax | MiniMax | MiniMax | ❌ |
| openai | GPT | OpenAI | ✅ |
| claude | Claude | Anthropic | ❌ |
| gemini | Gemini | Google | ✅ |

### 4.2 默认模型
- **DeepSeek** (deepseek-chat)

---

## 五、行业配置

### 5.1 支持的行业

| 行业ID | 名称 | 推荐模板 |
|-------|------|---------|
| education | 教育培训 | academic, nature, sky |
| medical | 医疗健康 | simple, nature, ocean |
| ecommerce | 电商零售 | gradient, festive, cyber |
| finance | 金融投资 | business, navy_gold, classic_blue |
| technology | 科技互联网 | tech, cyber, future |
| government | 政府企业 | enterprise, royal, academic |
| realestate | 房产建筑 | business, gray_elegant, ink_wash |
| media | 传媒广告 | gradient, cyber, royal |
| manufacture | 制造业 | enterprise, nature, classic_blue |
| general | 通用场景 | business, simple, elegant |

---

## 六、问题与建议

### 6.1 缺失项

1. ❌ **OpenAPI/Swagger文档** - 建议添加便于前后端协作
2. ❌ **API版本控制** - 当前所有端点无版本前缀（如 `/api/v1/`）
3. ❌ **API认证中间件** - 部分端点支持Token认证但未强制

### 6.2 安全建议

1. CORS配置为 `allow_origins=["*"]`，生产环境应限制
2. 部分敏感端点（如 `/api/auth/`）建议增加频率限制
3. 建议添加请求签名验证

### 6.3 性能优化建议

1. 知识库搜索建议添加缓存
2. 大文件下载建议支持断点续传
3. SSE长连接建议设置超时

---

## 七、端点统计

| 类别 | 数量 |
|-----|------|
| 总端点数 | 51 |
| GET | 21 |
| POST | 26 |
| PUT | 2 |
| DELETE | 2 |
