# DemoPPT E2E 测试套件

## 概述

本目录包含 DemoPPT v2.4 的端到端 (E2E) 测试和视觉回归测试。

## 测试文件结构

```
tests/e2e/
├── auth.spec.ts              # 用户注册/登录流程测试
├── ppt-generation.spec.ts    # AI生成PPT流程测试
├── template-selection.spec.ts # 模板选择功能测试
├── pricing.spec.ts           # 定价页面测试
├── visual-regression.spec.ts # 视觉回归测试
├── playwright.config.ts       # Playwright 配置
└── package.json              # 测试依赖
```

## 安装与运行

### 1. 安装依赖

```bash
cd tests/e2e
npm install
```

### 2. 安装 Playwright 浏览器

```bash
npx playwright install
```

### 3. 运行所有测试

```bash
npm test
```

### 4. 运行特定测试

```bash
# 运行登录测试
npx playwright test auth.spec.ts

# 运行视觉回归测试
npx playwright test visual-regression.spec.ts

# 运行带 UI 的测试
npm run test:ui
```

## 视觉回归测试

视觉基准截图保存在:

```
frontend/visual-tests/baseline/
├── homepage.png              # 首页
├── templates-page.png        # 模板选择页
├── pricing-page.png          # 定价页
├── pricing-page-with-plans.png # 定价页(含套餐)
├── ai-progress-page.png      # AI生成进度页
├── login-page.png            # 登录页
└── user-page.png             # 用户页
```

### 更新基准截图

```bash
npm run baseline
```

## 测试覆盖的流程

### 1. 用户注册/登录 (auth.spec.ts)
- 登录页面正确加载
- 新用户注册成功
- 已注册用户登录成功
- 错误密码显示错误提示
- 游客试用功能
- 退出登录功能

### 2. AI生成PPT (ppt-generation.spec.ts)
- Step 1: 需求收集 - 基础信息填写
- Step 1: 需求收集 - 角度与受众选择
- Step 1: 需求收集 - 可跳过参考资料
- Step 2: 确认大纲 - 大纲编辑功能
- Step 3: 选择模板 - 模板选择功能
- Step 3: 高级选项 - 品牌配置
- Step 4: 生成结果 - 成功页面结构

### 3. 模板选择 (template-selection.spec.ts)
- 首页模板展示
- 首页模板点击选择
- 首页快速生成
- 创建页面模板网格
- 模板预览样式
- 模板选择高亮

### 4. 定价页面 (pricing.spec.ts)
- 定价页面加载
- 套餐信息完整展示
- 推荐套餐标记
- 立即开通按钮状态
- 套餐特性列表
- 订单记录区域
- 响应式布局

## 前置条件

测试需要:
1. 后端服务运行在 `http://localhost:8000`
2. 前端服务运行在 `http://localhost:3000`

Playwright 配置的 `webServer` 会自动启动前端服务。

## 测试用户

测试使用以下测试账号:
- 手机号: `13800000000`
- 密码: `Test123456`

## 配置

可在 `playwright.config.ts` 中修改:
- 基础 URL
- 浏览器类型
- 超时设置
- 并行策略
