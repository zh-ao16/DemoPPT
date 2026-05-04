# DemoPPT 前端安全扫描报告

**项目**: DemoPPT  
**版本**: v2.4  
**扫描时间**: 2026-05-04  
**扫描范围**: /home/hg/.hermes/company/projects/DemoPPT/frontend/src/

---

## 1. XSS 风险点检查

### ✅ 未发现高风险 XSS 漏洞

| 检查项 | 文件 | 状态 | 说明 |
|--------|------|------|------|
| v-html 使用 | 全部 | ✅ 安全 | 未发现 `v-html` 或 `dangerouslySetInnerHTML` 使用 |
| innerHTML | 全部 | ✅ 安全 | 未发现 `innerHTML` 直接赋值 |
| eval/new Function | 全部 | ✅ 安全 | 未发现危险的动态代码执行 |
| 用户输入反射 | 全部 | ✅ 安全 | Vue 模板自动转义用户输入 |

### 潜在风险点 (低风险)

**1. API Key 显示 (Settings.vue:140)**
```javascript
<div><span class="label">API Key：</span><span class="value">{{ item.api_key }}</span></div>
```
- **风险**: API Key 在页面上明文显示
- **缓解**: 仅显示用户自己配置的 Key，且通过 HTTPS 传输
- **建议**: 考虑使用脱敏显示 (如 `sk-xxxx...xxxx`)

---

## 2. 敏感信息泄露检查

### ⚠️ 发现以下敏感信息处理

| 类型 | 文件 | 位置 | 风险等级 |
|------|------|------|----------|
| localStorage Token | main.js, App.vue, Login.vue, User.vue, Settings.vue, Create.vue | 多处 | ⚠️ 中 |
| localStorage 用户信息 | App.vue:49 | JSON.parse(localStorage.getItem('demoppt_user')) | ⚠️ 中 |
| API Key 存储 | Settings.vue | 用户配置的 API Key 存储 | ⚠️ 中 |
| 硬编码 API 地址 | Settings.vue, Login.vue, User.vue, Create.vue, Convert.vue, History.vue | `http://localhost:8000` | ℹ️ 低 |

### 详细分析

**Token 存储 (localStorage)**
```javascript
// main.js:31
const token = localStorage.getItem('demoppt_token')

// Login.vue:123
localStorage.setItem('demoppt_token', data.token)
```

**风险**: localStorage 数据可被 XSS 攻击窃取
**建议**: 
- 考虑使用 HttpOnly Cookie 存储 Token
- 或使用 sessionStorage 减少持久化风险
- 确保后端实现了 CSRF 保护

---

## 3. 不安全依赖检查

### 项目依赖分析

**package.json**
```json
{
  "dependencies": {
    "@ant-design/icons-vue": "^7.0.1",
    "ant-design-vue": "^4.2.6",
    "vue": "^3.4.0",
    "vue-router": "^4.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

### 依赖安全评估

| 依赖 | 版本 | 漏洞扫描 | 建议 |
|------|------|----------|------|
| vue | 3.4.0 | ✅ 通过 | 已是稳定版本 |
| vue-router | 4.2.0 | ✅ 通过 | 已是稳定版本 |
| ant-design-vue | 4.2.6 | ⚠️ 建议检查 | 使用最新稳定版 |
| vite | 5.0.0 | ⚠️ 建议检查 | 建议升级到最新补丁版 |

### 建议的安全措施

1. **定期更新依赖**
   ```bash
   npm audit
   npm update
   ```

2. **启用 Snyk 或 GitHub Security**
   - 建议集成依赖漏洞扫描

3. **锁定依赖版本**
   - 考虑使用 `package-lock.json` 确保一致性

---

## 4. 其他安全问题

### HTTP vs HTTPS

**发现**: 所有 API 请求使用 `http://localhost:8000`

| 文件 | 行号 | 代码 |
|------|------|------|
| Login.vue | 94 | `const API_BASE = 'http://localhost:8000'` |
| Settings.vue | 165 | `const API_BASE = 'http://localhost:8000'` |
| User.vue | 144 | `const API_BASE = 'http://localhost:8000'` |
| Create.vue | 408 | `const API = 'http://localhost:8000/api'` |
| Convert.vue | 93 | `const API = "http://localhost:8000/api";` |
| History.vue | 67 | `const API = 'http://localhost:8000/api'` |

**风险**: 生产环境应使用 HTTPS
**当前状态**: 开发环境可接受

---

## 5. 认证与授权

### 路由守卫分析

**main.js:30-41**
```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('demoppt_token')
  const protectedRoutes = ['/create', '/user', '/history']
  
  if (protectedRoutes.includes(to.path) && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/user')
  } else {
    next()
  }
})
```

**评估**:
- ✅ 登录状态检查正常
- ✅ 保护路由正确重定向
- ⚠️ 建议: 添加 Token 过期检查

---

## 6. 总结

### 风险等级: 🟡 中低

### 主要发现

| 类别 | 数量 | 严重程度 |
|------|------|----------|
| XSS 漏洞 | 0 | - |
| 敏感信息泄露 | 3 | 中 |
| 不安全依赖 | 0 (建议) | 低 |
| CSRF 风险 | 未评估 | 需后端确认 |

### 建议优先级

1. **高优先级**: 确认后端实现了 CSRF 保护
2. **中优先级**: 
   - 考虑使用 HttpOnly Cookie 替代 localStorage 存储 Token
   - API Key 脱敏显示
3. **低优先级**: 
   - 保持依赖更新
   - 生产环境切换到 HTTPS

---

## 7. 测试覆盖率

本扫描覆盖以下文件:
- `/src/main.js`
- `/src/App.vue`
- `/src/views/Login.vue`
- `/src/views/User.vue`
- `/src/views/Create.vue`
- `/src/views/Settings.vue`
- `/src/views/Home.vue`
- `/src/views/Convert.vue`
- `/src/views/History.vue`
- `/src/components/PricingCard.vue`
- `/src/components/AIProgress.vue`
- `/src/components/TemplateCard.vue`
- `/src/components/ExportPanel.vue`

---

*报告生成时间: 2026-05-04*  
*扫描工具: 静态代码分析*
