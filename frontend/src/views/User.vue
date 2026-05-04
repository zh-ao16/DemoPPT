<template>
  <div class="page-container">
    <!-- User Header -->
    <a-card :bordered="false" class="user-header-card">
      <a-row justify="space-between" align="middle">
        <a-col>
          <a-space>
            <div class="avatar">{{ userInfo.nickname?.charAt(0) || 'U' }}</div>
            <div class="user-info">
              <h2 class="nickname">{{ userInfo.nickname || '用户' }}</h2>
              <p class="phone">{{ formatPhone(userInfo.phone) }}</p>
            </div>
          </a-space>
        </a-col>
        <a-col>
          <a-button @click="logout">退出登录</a-button>
        </a-col>
      </a-row>
    </a-card>

    <!-- Subscription Section -->
    <a-card title="我的订阅" :bordered="false" class="section-card">
      <template #extra>
        <a-button v-if="subscription" type="link" @click="showPlans = true">续费/升级</a-button>
      </template>
      
      <div v-if="subscription" class="subscription-active">
        <a-row justify="space-between" align="middle" class="sub-header">
          <a-col>
            <a-space>
              <a-tag color="blue">{{ subscription.plan_name }}</a-tag>
              <span class="days-remaining">{{ subscription.days_remaining }}天</span>
            </a-space>
          </a-col>
          <a-col>
            <a-tag v-if="!subscription.is_expired" color="success">有效</a-tag>
            <a-tag v-else color="error">已过期</a-tag>
          </a-col>
        </a-row>
        
        <p class="sub-expire" v-if="!subscription.is_expired">
          有效期至：{{ subscription.end_time?.slice(0, 10) }}
        </p>
        <p class="sub-expire expired" v-else>
          订阅已过期
        </p>
        
        <div class="sub-features">
          <a-tag v-for="f in subscription.features" :key="f" color="purple">{{ f }}</a-tag>
        </div>
        
        <a-button 
          v-if="subscription.auto_renew === 1" 
          @click="cancelAutoRenew" 
          class="btn-cancel">
          关闭自动续费
        </a-button>
      </div>
      
      <a-empty v-else description="暂无订阅">
        <template #extra>
          <a-button type="primary" @click="showPlans = true">立即订阅</a-button>
        </template>
      </a-empty>
    </a-card>

    <!-- Plans Section -->
    <a-card 
      v-if="showPlans" 
      title="选择套餐" 
      :bordered="false" 
      class="section-card plans-card">
      <template #extra>
        <a-button type="link" @click="showPlans = false">关闭</a-button>
      </template>
      
      <a-row :gutter="[16, 16]">
        <a-col :xs="24" :sm="8" v-for="plan in plans" :key="plan.plan_code">
          <div 
            class="plan-card" 
            :class="{ recommended: plan.plan_code === 'yearly' }">
            <div v-if="plan.plan_code === 'yearly'" class="plan-badge">最优惠</div>
            <h4 class="plan-name">{{ plan.name }}</h4>
            <div class="plan-price">¥{{ plan.price_yuan }}</div>
            <p class="plan-duration">{{ plan.duration_days }}天</p>
            <ul class="plan-features">
              <li v-for="f in plan.features" :key="f">{{ f }}</li>
            </ul>
            <a-button 
              type="primary" 
              :disabled="subscription?.plan_code === plan.plan_code"
              @click="subscribe(plan.plan_code)"
              block>
              {{ subscription?.plan_code === plan.plan_code ? '当前套餐' : '立即开通' }}
            </a-button>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- Orders Section -->
    <a-card title="订单记录" :bordered="false" class="section-card">
      <a-empty v-if="orders.length === 0" description="暂无订单" />
      
      <a-list v-else :data-source="orders" item-layout="horizontal">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta
              :title="item.plan_name"
              :description="item.create_time?.slice(0, 10)"
            >
              <template #avatar>
                <a-avatar :style="{ backgroundColor: item.status === 'paid' ? '#52c41a' : '#faad14' }">
                  {{ item.status === 'paid' ? '✓' : '⏳' }}
                </a-avatar>
              </template>
            </a-list-item-meta>
            <template #actions>
              <span class="order-amount">¥{{ item.amount_yuan }}</span>
              <a-tag :color="item.status === 'paid' ? 'success' : 'warning'">
                {{ item.status === 'paid' ? '已支付' : item.status }}
              </a-tag>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- Pay Result Notification -->
    <a-notification
      v-if="payResult"
      :type="payResult.success ? 'success' : 'error'"
      :message="payResult.message"
      class="pay-notification"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE = 'http://localhost:8000'

const userInfo = ref({})
const subscription = ref(null)
const plans = ref([])
const orders = ref([])
const showPlans = ref(false)
const payResult = ref(null)

onMounted(async () => {
  const token = localStorage.getItem('demoppt_token')
  if (!token) {
    router.push('/login')
    return
  }
  
  const headers = { 'Authorization': `Bearer ${token}` }
  
  // 获取用户信息
  try {
    const meRes = await fetch(`${API_BASE}/api/auth/me`, { headers })
    const meData = await meRes.json()
    if (meData.success) {
      userInfo.value = meData.user
      subscription.value = meData.subscription
    }
  } catch (e) {}
  
  // 获取套餐列表
  try {
    const plansRes = await fetch(`${API_BASE}/api/plans`)
    const plansData = await plansRes.json()
    if (plansData.success) {
      plans.value = plansData.plans
    }
  } catch (e) {}
  
  // 获取订单列表
  try {
    const ordersRes = await fetch(`${API_BASE}/api/orders`, { headers })
    const ordersData = await ordersRes.json()
    if (ordersData.success) {
      orders.value = ordersData.orders || []
    }
  } catch (e) {}
})

async function subscribe(planCode) {
  const token = localStorage.getItem('demoppt_token')
  const headers = { 'Authorization': `Bearer ${token}` }
  
  try {
    // 创建订单
    const res = await fetch(`${API_BASE}/api/subscription/create?plan_code=${planCode}`, { 
      method: 'POST',
      headers 
    })
    const data = await res.json()
    
    if (data.success) {
      // 模拟支付
      const payRes = await fetch(`${API_BASE}/api/subscription/pay?order_id=${data.order_id}&transaction_id=SIM_${Date.now()}`, {
        method: 'POST'
      })
      const payData = await payRes.json()
      
      payResult.value = payData
      setTimeout(() => payResult.value = null, 3000)
      
      // 刷新订阅信息
      if (payData.success) {
        const meRes = await fetch(`${API_BASE}/api/auth/me`, { headers })
        const meData = await meRes.json()
        subscription.value = meData.subscription
        
        // 刷新订单
        const ordersRes = await fetch(`${API_BASE}/api/orders`, { headers })
        const ordersData = await ordersRes.json()
        if (ordersData.success) orders.value = ordersData.orders || []
        
        showPlans.value = false
      }
    }
  } catch (e) {
    payResult.value = { success: false, message: '支付失败，请重试' }
  }
}

async function cancelAutoRenew() {
  const token = localStorage.getItem('demoppt_token')
  const headers = { 'Authorization': `Bearer ${token}` }
  
  await fetch(`${API_BASE}/api/subscription/cancel`, { 
    method: 'POST',
    headers 
  })
  
  subscription.value.auto_renew = 0
}

function logout() {
  localStorage.removeItem('demoppt_token')
  localStorage.removeItem('demoppt_user')
  router.push('/')
}

function formatPhone(phone) {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.user-header-card {
  margin-bottom: 24px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.user-header-card :deep(.ant-card-body) {
  color: white;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.nickname {
  margin: 0 0 4px;
  font-size: 18px;
  color: white;
}

.phone {
  margin: 0;
  font-size: 14px;
  color: rgba(255,255,255,0.9);
}

.user-header-card :deep(.ant-btn) {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
}

.user-header-card :deep(.ant-btn:hover) {
  background: rgba(255,255,255,0.3);
  border-color: rgba(255,255,255,0.4);
  color: white;
}

.section-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.subscription-active {
  padding: 16px;
  background: #f8f5ff;
  border-radius: 8px;
  border: 1px solid #d3adf7;
}

.sub-header {
  margin-bottom: 12px;
}

.days-remaining {
  font-size: 24px;
  font-weight: bold;
  color: #722ed1;
}

.sub-expire {
  color: #8c8c8c;
  font-size: 14px;
  margin-bottom: 12px;
}

.sub-expire.expired {
  color: #ff4d4f;
}

.sub-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.btn-cancel {
  margin-top: 8px;
}

.plans-card :deep(.ant-card-head) {
  border-bottom: none;
}

.plan-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  position: relative;
  transition: all 0.3s;
  height: 100%;
}

.plan-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}

.plan-card.recommended {
  border-color: #1890ff;
  box-shadow: 0 4px 20px rgba(24, 144, 255, 0.2);
}

.plan-badge {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 10px;
  font-size: 12px;
}

.plan-name {
  margin: 0 0 12px;
  font-size: 16px;
}

.plan-price {
  font-size: 28px;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 4px;
}

.plan-duration {
  color: #8c8c8c;
  font-size: 13px;
  margin: 0 0 16px;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  text-align: left;
}

.plan-features li {
  padding: 6px 0;
  font-size: 13px;
  color: #595959;
  border-bottom: 1px solid #f0f0f0;
}

.plan-features li:last-child {
  border-bottom: none;
}

.plan-features li::before {
  content: '✓';
  color: #52c41a;
  margin-right: 6px;
}

.order-amount {
  font-weight: bold;
  color: #262626;
  margin-right: 16px;
}

.pay-notification {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 1000;
}
</style>
