# DemoPPT v2.4 Vue3组件分析报告

**生成时间：** 2026-05-04  
**版本：** v2.4

---

## 一、现有组件分析

### 1.1 组件目录状态

**路径：** `/home/hg/.hermes/company/projects/DemoPPT/frontend/src/components/`

**发现：** ❌ 组件目录为空

目前前端项目**没有任何可复用组件**，所有UI代码都直接写在`views/`目录下的页面组件中。

### 1.2 现有视图结构

| 视图文件 | 功能描述 |
|---------|---------|
| `Home.vue` | 首页/工作台 |
| `Create.vue` | PPT创建页面 |
| `History.vue` | 历史记录 |
| `Convert.vue` | 文档转换 |
| `Login.vue` | 登录页 |
| `User.vue` | 用户中心 |
| `Settings.vue` | 设置页 |

### 1.3 技术栈

- **框架：** Vue 3
- **UI库：** Ant Design Vue
- **构建工具：** Vite
- **路由：** Vue Router

---

## 二、痛点驱动的新增组件建议

根据PRD和痛点报告，**AI生成质量**和**模板质量**是最严重的问题（5星优先级）。需要针对性的UI组件来改善这些问题。

### 2.1 AI生成质量提升组件（P0优先级）

#### 🔴 建议1：AIContentPreview 内容预览组件

**问题背景：** 用户痛点——"AI生成内容空洞、逻辑混乱"

**功能需求：**
- 支持分段预览AI生成的内容
- 支持实时编辑和反馈
- 显示内容质量指标（字数、结构完整性等）
- 支持一键优化/重生成

**接口依赖：**
```javascript
POST /api/preview_content
Request: { topic, subtitle, industry, page_title, page_type }
Response: { success, content: string[] }
```

**组件规格：**
```vue
<AIContentPreview
  :topic="form.topic"
  :industry="form.industry"
  :page-title="currentPage.title"
  @update:content="handleContentUpdate"
  @regenerate="handleRegenerate"
/>
```

#### 🔴 建议2：OutlineEditor 大纲编辑器组件

**问题背景：** 用户痛点——"AI生成内容缺乏逻辑性"

**功能需求：**
- 可视化大纲编辑
- 支持拖拽排序
- 支持增删章节
- 显示大纲结构预览
- 实时保存草稿

**接口依赖：**
```javascript
POST /api/generate_outline
Request: { topic, requirements, industry, model_config_id }
Response: { success, outline: [{title, type}], has_kb_context }
```

#### 🔴 建议3：QualityScore 质量评分组件

**问题背景：** 验证AI生成质量达标（PRD验收标准：≥4.5/5.0）

**功能需求：**
- 显示内容质量评分
- 分类评分（逻辑性、实用性、原创性）
- 标注潜在问题
- 提供改进建议

---

### 2.2 模板质量提升组件（P0优先级）

#### 🔴 建议4：TemplateGallery 模板画廊组件

**问题背景：** 用户痛点——"模板质量参差不齐，精品模板少"

**功能需求：**
- 网格/列表双视图切换
- 分类筛选（行业/风格/场景）
- 搜索功能
- 模板质量评分显示
- 16:9/4:3双比例预览
- 深色模式预览
- 收藏功能

**接口依赖：**
```javascript
GET /api/templates
Response: { templates: [...] }

GET /api/color_palettes
Response: { palettes: [...] }
```

**组件规格：**
```vue
<TemplateGallery
  :industry="form.industry"
  :show-quality-score="true"
  @select="handleTemplateSelect"
/>
```

#### 🔴 建议5：TemplatePreview 模板预览弹窗组件

**问题背景：** 用户痛点——"模板预览占位图需要修复"

**功能需求：**
- 全屏预览模式
- 幻灯片翻页浏览
- 缩略图导航
- 深色模式切换
- 模板详情信息展示

**模板ID列表（12款）：**
| ID | 名称 | 场景 |
|----|------|------|
| business | 商务蓝 | 企业汇报 |
| academic | 学术风 | 学术报告 |
| tech | 科技风 | 科技展示 |
| enterprise | 企业蓝 | 企业宣传 |
| cyber | 赛博朋克 | 创意展示 |
| gradient | 渐变风 | 营销推广 |
| nature | 商务绿 | 环保健康 |
| ocean | 海洋蓝 | 旅行海洋 |
| elegant | 商务紫 | 高端定制 |
| royal | 皇家紫 | 高端场合 |
| festive | 商务红 | 庆典节日 |
| chinese | 中国风 | 传统文化 |

---

### 2.3 核心交互组件（P1优先级）

#### 🟡 建议6：GenerationProgress 生成进度组件

**问题背景：** AI生成时间较长（≤10秒/单页，≤60秒/完整PPT），需要良好进度反馈

**功能需求：**
- 实时进度条
- 当前阶段显示
- 预计剩余时间
- 错误提示和处理
- 取消生成功能

**接口依赖：**
```javascript
GET /api/progress/{session_id}  // SSE流
Response: { stage, progress, message }
```

#### 🟡 建议7：BrandCustomizer 品牌定制组件

**问题背景：** PRD需求——品牌定制功能

**功能需求：**
- 品牌名称输入
- Logo上传/预览
- 自定义主题色选择器
- 实时预览效果

**接口依赖：**
```javascript
POST /api/preview_palette
Request: { colors, template }
```

#### 🟡 建议8：IndustrySelector 行业选择器组件

**功能需求：**
- 行业分类导航
- 推荐模板展示
- 行业知识上下文提示

**行业列表（10个）：**
- 教育培训、医疗健康、电商零售、金融投资
- 科技互联网、政府企业、房产建筑、传媒广告
- 制造业、通用场景

---

## 三、组件开发优先级

| 优先级 | 组件名称 | 功能 | 痛点对应 |
|-------|---------|------|---------|
| P0 | `AIContentPreview` | AI内容预览+反馈 | AI生成质量 |
| P0 | `OutlineEditor` | 大纲编辑优化 | AI生成质量 |
| P0 | `TemplateGallery` | 模板选择画廊 | 模板质量 |
| P0 | `TemplatePreview` | 模板预览弹窗 | 模板质量 |
| P1 | `GenerationProgress` | 生成进度条 | 体验优化 |
| P1 | `BrandCustomizer` | 品牌定制 | 差异化功能 |
| P1 | `IndustrySelector` | 行业选择器 | 中文支持 |
| P2 | `QualityScore` | 质量评分 | AI生成质量验证 |

---

## 四、技术实现建议

### 4.1 组件目录结构
```
frontend/src/components/
├── ai/
│   ├── AIContentPreview.vue
│   ├── OutlineEditor.vue
│   └── QualityScore.vue
├── template/
│   ├── TemplateGallery.vue
│   └── TemplatePreview.vue
├── common/
│   ├── GenerationProgress.vue
│   ├── BrandCustomizer.vue
│   └── IndustrySelector.vue
└── index.js  // 统一导出
```

### 4.2 共享样式
建议创建 `assets/styles/brand.css` 统一管理CSS变量：
```css
:root {
  --color-brand: #2563EB;
  --color-brand-light: #DBEAFE;
  --color-brand-dark: #1D4ED8;
  /* ... 其他变量 */
}
```

### 4.3 API接口一览

| 端点 | 方法 | 功能 |
|-----|------|------|
| `/api/generate_outline` | POST | 生成大纲 |
| `/api/preview_content` | POST | 单页内容预览 |
| `/api/progress/{session_id}` | GET | SSE生成进度 |
| `/api/templates` | GET | 获取模板列表 |
| `/api/color_palettes` | GET | 获取配色方案 |
| `/api/preview_palette` | POST | 预览配色效果 |
| `/api/industries` | GET | 获取行业列表 |

---

## 五、注意事项

1. **品牌色修复：** 设计规范P0项提到需要将 `#667eea` 替换为 `#2563EB`
2. **模板统一：** 前后端模板定义需统一为12款
3. **组件库选择：** 继续使用Ant Design Vue，避免重复造轮子
4. **响应式设计：** 遵循设计规范中的PC/移动端适配规则
