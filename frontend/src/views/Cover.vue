<template>
  <div class="page-container">
    <a-card title="🎨 封面生成器" :bordered="false" class="main-card">
      <template #extra>
        <router-link to="/">
          <a-button>返回首页</a-button>
        </router-link>
      </template>

      <div class="cover-preview">
        <div class="preview-area" :style="previewStyle">
          <div class="preview-deco-circle circle1"></div>
          <div class="preview-deco-circle circle2"></div>
          <div class="preview-title">{{ topic || '请输入封面主题' }}</div>
          <div class="preview-subtitle">{{ currentSubtitle }}</div>
          <div class="preview-logo">YOUR LOGO</div>
        </div>
      </div>

      <a-divider>封面设置</a-divider>

      <a-form layout="vertical" :model="form">
        <a-form-item label="封面主题">
          <a-input
            v-model:value="form.topic"
            placeholder="例如：夏日穿搭指南、职场晋升攻略"
            size="large"
            @change="updatePreview"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="封面风格">
              <a-select v-model:value="form.style" size="large" @change="updatePreview">
                <a-select-option value="时尚感">🎀 时尚感</a-select-option>
                <a-select-option value="简约风">🧘 简约风</a-select-option>
                <a-select-option value="节日感">🎉 节日感</a-select-option>
                <a-select-option value="商务风">💼 商务风</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="平台类型">
              <a-select v-model:value="form.platform" size="large" @change="updatePreview">
                <a-select-option value="小红书">📕 小红书</a-select-option>
                <a-select-option value="公众号">📱 公众号</a-select-option>
                <a-select-option value="朋友圈">📸 朋友圈</a-select-option>
                <a-select-option value="微博">🌐 微博</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="图片比例">
          <a-radio-group v-model:value="form.aspect" button-style="solid" @change="updatePreview">
            <a-radio-button value="3:4">3:4 竖图（小红书最佳）</a-radio-button>
            <a-radio-button value="16:9">16:9 横图</a-radio-button>
          </a-radio-group>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" size="large" block :loading="loading" @click="generateCover">
            🎨 一键生成封面
          </a-button>
        </a-form-item>

        <a-form-item v-if="downloadUrl">
          <a-button type="primary" size="large" block @click="downloadFile">
            📥 下载封面PPT
          </a-button>
        </a-form-item>
      </a-form>

      <a-divider>封面比例参考</a-divider>
      <a-row :gutter="16" class="size-info">
        <a-col :span="12">
          <div class="size-card">
            <div class="size-preview size-3-4"></div>
            <div class="size-label">
              <strong>3:4 竖图</strong>
              <p>1280 × 1706 px</p>
              <p class="tip">小红书封面最佳尺寸</p>
            </div>
          </div>
        </a-col>
        <a-col :span="12">
          <div class="size-card">
            <div class="size-preview size-16-9"></div>
            <div class="size-label">
              <strong>16:9 横图</strong>
              <p>1920 × 1080 px</p>
              <p class="tip">公众号/微博横幅</p>
            </div>
          </div>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'

const form = reactive({
  topic: '',
  style: '时尚感',
  platform: '小红书',
  aspect: '3:4'
})

const loading = ref(false)
const downloadUrl = ref('')

const styleColors = {
  '时尚感': { bg: '#FF6B9D', accent: '#FFD93D', subtitle: '#FFE4EC' },
  '简约风': { bg: '#2C3E50', accent: '#ECF0F1', subtitle: '#BDC3C7' },
  '节日感': { bg: '#E74C3C', accent: '#F1C40F', subtitle: '#FDEBD0' },
  '商务风': { bg: '#1A365D', accent: '#ED8936', subtitle: '#CBD5E0' }
}

const platformTags = {
  '小红书': '📕 分享美好生活',
  '公众号': '📱 关注了解更多',
  '朋友圈': '📸 记录精彩瞬间',
  '微博': '🌐 发现新鲜事'
}

const previewStyle = computed(() => {
  const colors = styleColors[form.style] || styleColors['时尚感']
  const isVertical = form.aspect === '3:4'
  return {
    background: colors.bg,
    aspectRatio: isVertical ? '3 / 4' : '16 / 9',
    maxHeight: '400px'
  }
})

const currentSubtitle = computed(() => {
  return platformTags[form.platform] || '✨ 精彩内容'
})

const updatePreview = () => {
  downloadUrl.value = ''
}

const generateCover = async () => {
  if (!form.topic.trim()) {
    message.warning('请输入封面主题')
    return
  }

  loading.value = true
  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
    const res = await fetch(`${API_BASE}/api/generate_cover`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: form.topic,
        style: form.style,
        aspect: form.aspect
      })
    })
    const data = await res.json()
    
    if (data.success) {
      downloadUrl.value = `${API_BASE}${data.download_url}`
      message.success('封面生成成功！')
    } else {
      message.error(data.message || '生成失败')
    }
  } catch (e) {
    message.error('网络错误，请重试')
  } finally {
    loading.value = false
  }
}

const downloadFile = () => {
  if (downloadUrl.value) {
    window.open(downloadUrl.value, '_blank')
  }
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.main-card {
  border-radius: 8px;
  max-width: 800px;
  margin: 0 auto;
}

.cover-preview {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.preview-area {
  position: relative;
  width: 100%;
  max-width: 300px;
  min-height: 300px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: all 0.3s;
}

.preview-deco-circle {
  position: absolute;
  border-radius: 50%;
}

.circle1 {
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.3);
  top: -30px;
  right: -30px;
}

.circle2 {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  bottom: -15px;
  left: -15px;
}

.preview-title {
  font-size: 20px;
  font-weight: bold;
  color: white;
  text-align: center;
  padding: 0 20px;
  z-index: 1;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.preview-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 12px;
  z-index: 1;
}

.preview-logo {
  position: absolute;
  bottom: 15px;
  right: 15px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  z-index: 1;
}

.size-info {
  margin-top: 16px;
}

.size-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.size-preview {
  background: #ddd;
  border: 2px dashed #ccc;
  border-radius: 4px;
}

.size-3-4 {
  width: 60px;
  height: 80px;
}

.size-16-9 {
  width: 80px;
  height: 45px;
}

.size-label strong {
  display: block;
  margin-bottom: 4px;
}

.size-label p {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.size-label .tip {
  color: #1890ff;
  font-size: 11px;
  margin-top: 4px;
}
</style>
