<template>
  <div class="page-container">
    <!-- Hero Section -->
    <a-card class="hero-card" :bordered="false">
      <div class="hero-content">
        <h1 class="hero-title">AI智能PPT <span class="highlight">行业解决方案</span></h1>
        <p class="hero-subtitle">输入主题生成 或 文档一键转换，10大行业模板+AI数字人</p>
        
        <div class="cta-section">
          <a-input-search
            v-model:value="topic"
            placeholder="输入你的PPT主题"
            size="large"
            class="topic-search"
            @search="startCreate"
            @keyup.enter="startCreate">
            <template #enterButton>
              <a-button type="primary" size="large">智能生成</a-button>
            </template>
          </a-input-search>
        </div>
        
        <div class="cta-secondary">
          <router-link to="/convert">
            <a-button size="large" ghost>📄 文档一键转PPT</a-button>
          </router-link>
        </div>
        
        <a-row :gutter="[60, 24]" justify="center" class="stats-row">
          <a-col>
            <div class="stat-item">
              <span class="stat-num">21</span>
              <span class="stat-label">精选模板</span>
            </div>
          </a-col>
          <a-col>
            <div class="stat-item">
              <span class="stat-num">10</span>
              <span class="stat-label">行业方案</span>
            </div>
          </a-col>
          <a-col>
            <div class="stat-item">
              <span class="stat-num">3秒</span>
              <span class="stat-label">生成大纲</span>
            </div>
          </a-col>
          <a-col>
            <div class="stat-item">
              <span class="stat-num">AI</span>
              <span class="stat-label">数字人</span>
            </div>
          </a-col>
        </a-row>
      </div>
    </a-card>

    <!-- Industries Section -->
    <a-card title="🎯 10大行业解决方案" :bordered="false" class="section-card">
      <div class="industry-grid">
        <a-tag 
          v-for="ind in industries" 
          :key="ind.id" 
          :color="ind.color"
          class="industry-tag">
          <span class="ind-icon">{{ ind.icon }}</span>
          <span class="ind-name">{{ ind.name }}</span>
        </a-tag>
      </div>
    </a-card>

    <!-- Features Section -->
    <a-card title="为什么选择 DemoPPT？" :bordered="false" class="section-card">
      <a-row :gutter="[24, 24]">
        <a-col :xs="24" :sm="12" :md="8" v-for="feature in features" :key="feature.title">
          <div class="feature-card">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.desc }}</p>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- Templates Section -->
    <a-card title="精选模板库" :bordered="false" class="section-card">
      <a-row :gutter="[16, 16]">
        <a-col :xs="12" :sm="8" :md="4" v-for="t in templates" :key="t.id">
          <div 
            class="template-item" 
            :class="{ active: selectedTemplate === t.id }"
            @click="selectedTemplate = t.id">
            <div class="template-preview" :style="{ background: t.color }">
              <span>{{ t.name }}</span>
            </div>
            <p class="template-desc">{{ t.desc }}</p>
          </div>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'

const router = useRouter()
const topic = ref('')
const selectedTemplate = ref('business')

const industries = [
  { id: 'education', icon: '🎓', name: '教育培训', color: 'green' },
  { id: 'medical', icon: '🏥', name: '医疗健康', color: 'blue' },
  { id: 'ecommerce', icon: '🛒', name: '电商零售', color: 'red' },
  { id: 'finance', icon: '💰', name: '金融投资', color: 'blue' },
  { id: 'technology', icon: '💻', name: '科技互联网', color: 'purple' },
  { id: 'government', icon: '🏛️', name: '政府企业', color: 'purple' },
  { id: 'realestate', icon: '🏗️', name: '房产建筑', color: 'orange' },
  { id: 'media', icon: '📺', name: '传媒广告', color: 'magenta' },
  { id: 'manufacture', icon: '⚙️', name: '制造业', color: 'cyan' },
  { id: 'general', icon: '📋', name: '通用场景', color: 'default' },
]

const features = [
  { icon: '🎯', title: '内容有深度', desc: '接入DeepSeek/豆包AI，生成有逻辑、有观点的实质内容' },
  { icon: '📄', title: '文档一键转PPT', desc: 'Word/PDF/TXT直接上传，AI自动分析结构并生成专业PPT' },
  { icon: '🏭', title: '行业定制模板', desc: '10大行业专属配色和布局，教育/医疗/金融/电商等量身打造' },
  { icon: '🎨', title: '21款高颜值模板', desc: '学术风、商务风、科技风、中国风... 满足各种场景' },
  { icon: '⚡', title: '速度快', desc: '输入主题，3秒出大纲，2分钟生成完整PPT' },
  { icon: '🎥', title: 'AI数字人播报', desc: '可选虚拟主播，自动生成讲解稿，让PPT开口说话' },
]

const templates = [
  { id: 'business', name: '商务蓝', desc: '藏蓝金色', color: 'linear-gradient(135deg, #2c5282, #ed8936)' },
  { id: 'academic', name: '学术风', desc: '深蓝白色', color: 'linear-gradient(135deg, #1a365d, #2c5282)' },
  { id: 'enterprise', name: '企业蓝', desc: '稳重企业', color: 'linear-gradient(135deg, #1e3a5f, #3182ce)' },
  { id: 'tech', name: '科技风', desc: '蓝紫渐变', color: 'linear-gradient(135deg, #1a1a4e, #00d4ff)' },
  { id: 'cyber', name: '赛博朋克', desc: '霓虹科技', color: 'linear-gradient(135deg, #0f0f23, #ff00ff)' },
  { id: 'gradient', name: '渐变风', desc: '彩色活力', color: 'linear-gradient(135deg, #ff6b6b, #4ecdc4)' },
  { id: 'nature', name: '商务绿', desc: '绿色清新', color: 'linear-gradient(135deg, #276749, #68d391)' },
  { id: 'ocean', name: '海洋蓝', desc: '清爽海风', color: 'linear-gradient(135deg, #0077b6, #00b4d8)' },
  { id: 'elegant', name: '商务紫', desc: '紫色高贵', color: 'linear-gradient(135deg, #553c9a, #9f7aea)' },
  { id: 'royal', name: '皇家紫', desc: '皇室贵族', color: 'linear-gradient(135deg, #4c1d95, #8b5cf6)' },
  { id: 'festive', name: '商务红', desc: '红色喜庆', color: 'linear-gradient(135deg, #c53030, #fc8181)' },
  { id: 'chinese', name: '中国风', desc: '水墨文化', color: 'linear-gradient(135deg, #1a202c, #718096)' },
]

const startCreate = () => {
  if (!topic.value.trim()) {
    message.warning('请输入PPT主题')
    return
  }
  router.push({ path: '/create', query: { topic: topic.value, template: selectedTemplate.value } })
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.hero-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.hero-content {
  text-align: center;
  padding: 40px 20px;
}

.hero-title {
  font-size: 28px;
  margin-bottom: 16px;
  color: #262626;
}

.highlight {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 16px;
  color: #8c8c8c;
  margin-bottom: 32px;
}

.cta-section {
  max-width: 600px;
  margin: 0 auto 16px;
}

.topic-search {
  width: 100%;
}

.cta-secondary {
  margin-bottom: 40px;
}

.stats-row {
  margin-top: 24px;
}

.stat-item {
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 32px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  color: #8c8c8c;
  font-size: 14px;
}

.section-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.industry-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.industry-tag {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
}

.ind-icon {
  margin-right: 8px;
}

.feature-card {
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
  height: 100%;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 16px;
  margin-bottom: 8px;
  color: #262626;
}

.feature-desc {
  font-size: 14px;
  color: #8c8c8c;
  line-height: 1.6;
  margin: 0;
}

.template-item {
  text-align: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.template-item:hover {
  background: #f5f5f5;
}

.template-item.active .template-preview {
  box-shadow: 0 0 0 3px #1890ff;
}

.template-preview {
  height: 70px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 12px;
  margin-bottom: 8px;
}

.template-desc {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0;
}
</style>
