# DemoPPT - AI 智能演示文稿生成平台

**在线访问：** https://demoppt-ivvb683tm-zh-ao16s-projects.vercel.app

> 输入主题，AI 自动生成专业 PPT。支持内容生成、模板切换、中文排版、演讲者备注、数据可视化、文档导入。

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **AI 内容生成** | 输入任意主题，自动生成结构完整的 PPT 内容 |
| **28+ 精选模板** | 覆盖商务、教育、技术、创意等场景，支持一键切换 |
| **中文排版优化** | 中文标点、段落缩进、避头避尾策略专业级处理 |
| **演讲者备注** | 每页自动生成演讲者备注，方便演讲准备 |
| **品牌定制** | 上传品牌色，一键应用品牌风格 |
| **文档导入** | 支持导入 Word/PDF/TXT 文档内容 |
| **AI 内容润色** | 对生成内容进行续写、润色、缩写 |
| **模板中心** | 浏览、下载、上传分享模板 |
| **小红书封面** | 输入主题，生成小红书封面图 |
| **演示者模式** | 大屏投影模式，配合演讲者备注使用 |
| **划词翻译** | 选中页面文字，一键翻译 |
| **知识库 RAG** | 上传内部文档，构建专属知识库 |
| **联网搜索** | 自动搜索最新信息补充内容 |

---

## 订阅套餐

| 套餐 | 价格 | 说明 |
|------|------|------|
| 月卡 | ¥99 / 月 | 每日 100 次生成 |
| 季卡 | ¥249 / 季 | 每日 200 次生成 |
| 年卡 | ¥799 / 年 | 每日 500 次生成 |

---

## 技术架构

```
前端：Vue 3 + Vite + Ant Design Vue
后端：Python FastAPI
PPT 引擎：python-pptx
模板：28+ 精选设计模板
部署：Vercel（前端）+ 独立服务器（后端）
```

---

## 本地开发

### 环境要求

- Python 3.9+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 访问地址

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/api/docs

---

## 项目结构

```
DemoPPT/
├── backend/                 # Python FastAPI 后端
│   ├── main.py             # 主应用入口
│   ├── user_auth.py        # 用户注册/登录/Token
│   ├── subscription.py     # 订阅套餐管理
│   ├── api_auth.py         # Token 鉴权中间件
│   ├── routes/             # API 路由
│   └── templates/          # PPT 模板文件
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── style/         # 全局样式
│   └── package.json
├── templates/              # 模板资源
├── tests/                 # 测试文件
└── vercel.json           # Vercel 部署配置
```

---

## API 文档

详细 API 文档请访问：`http://localhost:8000/api/docs`

主要接口：

- `POST /api/chat` - AI 生成 PPT 内容
- `POST /api/generate` - 生成 PPT 文件
- `GET /api/templates` - 获取模板列表
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `GET /api/subscription` - 订阅信息

---

## 技术亮点

- **python-pptx 渲染引擎**：基于原生 PPTX 格式，非 HTML 转换，确保最佳兼容性和打印质量
- **中文排版引擎**：专业中文排版规则处理（标点压缩、避头避尾、繁简转换）
- **多 LLM 支持**：OpenAI / MiniMax / DeepSeek 等多模型自由切换
- **流式生成**：支持 SSE 流式输出，实时展示生成进度
- **模板系统**：多种场景模板，前端实时切换，所见即所得

---

## 更新日志

### v2.5（2026-05-05）
- 新增模板中心（浏览/下载/上传分享）
- 新增小红书封面生成器
- 新增演示者模式
- 新增划词翻译功能
- 新增 5 个技术场景模板（代码/算法/架构/调试/文档）
- 修复注册登录验证码流程
- 部署至 Vercel

### v2.4（2026-05-04）
- 用户注册/登录系统
- 订阅套餐管理
- 支付模块基础架构
- Token 鉴权体系

### v2.3（2026-05-03）
- 现代风格模板
- Word/PDF/TXT 文档导入
- AI 内容润色
- 向导式信息收集
- 知识库 RAG
- 联网搜索

---

## License

MIT License
