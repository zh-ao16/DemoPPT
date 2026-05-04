<template>
  <div class="login-page">
    <div class="login-container">
      <a-card class="login-card" :bordered="false">
        <div class="login-header">
          <h1>DemoPPT</h1>
          <p>AI智能PPT生成系统</p>
        </div>
        
        <a-tabs v-model:activeKey="tab" class="login-tabs">
          <a-tab-pane key="login" tab="登录" />
          <a-tab-pane key="register" tab="注册" />
        </a-tabs>
        
        <!-- Login Form -->
        <a-form 
          v-if="tab === 'login'" 
          layout="vertical" 
          class="login-form"
          @finish="handleLogin">
          <a-form-item label="手机号" name="phone">
            <a-input 
              v-model:value="phone" 
              placeholder="请输入手机号" 
              size="large"
              :maxlength="11">
              <template #prefix>
                <span class="input-icon">📱</span>
              </template>
            </a-input>
          </a-form-item>
          <a-form-item label="密码" name="password">
            <a-input-password 
              v-model:value="password" 
              placeholder="请输入密码" 
              size="large" />
          </a-form-item>
          <a-alert v-if="error" type="error" :message="error" show-icon class="error-alert" />
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">
            {{ loading ? '登录中...' : '登录' }}
          </a-button>
        </a-form>
        
        <!-- Register Form -->
        <a-form 
          v-else 
          layout="vertical" 
          class="login-form"
          @finish="handleRegister">
          <a-form-item label="手机号" name="phone">
            <a-input 
              v-model:value="phone" 
              placeholder="请输入手机号" 
              size="large"
              :maxlength="11">
              <template #prefix>
                <span class="input-icon">📱</span>
              </template>
            </a-input>
          </a-form-item>
          <a-form-item label="密码" name="password">
            <a-input-password 
              v-model:value="password" 
              placeholder="请输入密码（至少6位）" 
              size="large" />
          </a-form-item>
          <a-form-item label="昵称（选填）" name="nickname">
            <a-input 
              v-model:value="nickname" 
              placeholder="请输入昵称" 
              size="large"
              :maxlength="20" />
          </a-form-item>
          <a-alert v-if="error" type="error" :message="error" show-icon class="error-alert" />
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">
            {{ loading ? '注册中...' : '注册' }}
          </a-button>
        </a-form>
        
        <div class="login-footer">
          <a @click="goHome" class="link">游客试用</a>
          <a v-if="isLoggedIn" @click="logout" class="link">退出</a>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE = 'http://localhost:8000'

const tab = ref('login')
const phone = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const loading = ref(false)

const isLoggedIn = computed(() => !!localStorage.getItem('demoppt_token'))

onMounted(() => {
  if (isLoggedIn.value) {
    router.push('/user')
  }
})

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: phone.value, password: password.value })
    })
    const data = await res.json()
    
    if (data.success) {
      localStorage.setItem('demoppt_token', data.token)
      localStorage.setItem('demoppt_user', JSON.stringify({
        id: data.user_id,
        nickname: data.nickname,
        phone: phone.value
      }))
      router.push('/user')
    } else {
      error.value = data.error || '登录失败'
    }
  } catch (e) {
    error.value = '网络错误，请重试'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: phone.value, password: password.value, nickname: nickname.value })
    })
    const data = await res.json()
    
    if (data.success) {
      localStorage.setItem('demoppt_token', data.token)
      localStorage.setItem('demoppt_user', JSON.stringify({
        id: data.user_id,
        nickname: nickname.value || `用户${phone.value.slice(-4)}`,
        phone: phone.value
      }))
      router.push('/user')
    } else {
      error.value = data.error || '注册失败'
    }
  } catch (e) {
    error.value = '网络错误，请重试'
  } finally {
    loading.value = false
  }
}

function goHome() {
  router.push('/')
}

function logout() {
  localStorage.removeItem('demoppt_token')
  localStorage.removeItem('demoppt_user')
  router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 0 16px;
}

.login-card {
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-card :deep(.ant-card-body) {
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-header h1 {
  font-size: 28px;
  color: #262626;
  margin: 0 0 8px;
}

.login-header p {
  color: #8c8c8c;
  margin: 0;
  font-size: 14px;
}

.login-tabs {
  margin-bottom: 24px;
}

.login-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

.login-form {
  margin-bottom: 16px;
}

.login-form :deep(.ant-form-item) {
  margin-bottom: 20px;
}

.login-form :deep(.ant-form-item-label) {
  padding-bottom: 8px;
}

.input-icon {
  font-size: 16px;
}

.error-alert {
  margin-bottom: 16px;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.link {
  color: #1890ff;
  cursor: pointer;
  font-size: 13px;
}

.link:hover {
  color: #40a9ff;
}
</style>
