<template>
  <div id="app">
    <header class="header">
      <div class="logo" @click="$router.push('/')">DemoPPT</div>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/create">创建PPT</router-link>
        <router-link to="/convert">文档转PPT</router-link>
        <router-link to="/history">我的历史</router-link>
        <router-link to="/settings">模型配置</router-link>
        <router-link v-if="isLoggedIn" to="/user" class="user-link">
          <span class="user-icon">{{ userNickname?.charAt(0) || 'U' }}</span>
          {{ userNickname }}
        </router-link>
        <router-link v-else to="/login" class="login-link">登录</router-link>
      </nav>
    </header>
    <main class="main">
      <router-view />
    </main>
    <footer class="footer">
      <p>DemoTech AI  让PPT制作变得简单</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      isLoggedIn: false,
      userNickname: ''
    }
  },
  mounted() {
    this.checkLogin()
    // 监听登录状态变化
    window.addEventListener('storage', this.checkLogin)
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.checkLogin)
  },
  methods: {
    checkLogin() {
      const token = localStorage.getItem('demoppt_token')
      this.isLoggedIn = !!token
      if (token) {
        const user = JSON.parse(localStorage.getItem('demoppt_user') || '{}')
        this.userNickname = user.nickname || '用户'
      } else {
        this.userNickname = ''
      }
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; color: #333; }
#app { min-height: 100vh; display: flex; flex-direction: column; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0 40px; height: 60px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 24px; font-weight: bold; color: white; cursor: pointer; }
.nav { display: flex; gap: 30px; align-items: center; }
.nav a { color: rgba(255,255,255,0.9); text-decoration: none; font-size: 16px; }
.nav a:hover, .nav a.router-link-active { color: white; }
.login-link { background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 20px; }
.user-link { display: flex; align-items: center; gap: 6px; }
.user-icon { width: 28px; height: 28px; background: rgba(255,255,255,0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; }
.main { flex: 1; padding: 40px; max-width: 1400px; margin: 0 auto; width: 100%; }
.footer { text-align: center; padding: 20px; color: #999; font-size: 14px; }
.btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
.btn-secondary { background: white; color: #667eea; border: 2px solid #667eea; padding: 10px 28px; border-radius: 8px; cursor: pointer; }
.btn-secondary:hover { background: #667eea; color: white; }
.card { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
</style>
