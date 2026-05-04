<template>
  <div class="presenter-container">
    <!-- Header -->
    <div class="presenter-header">
      <div class="header-left">
        <router-link to="/history">
          <a-button type="text" size="large">← 返回</a-button>
        </router-link>
        <span class="filename">{{ filename }}</span>
      </div>
      <div class="header-center">
        <span class="page-indicator">{{ currentPage + 1 }} / {{ totalPages }}</span>
      </div>
      <div class="header-right">
        <span class="user-info" v-if="currentUser">👤 {{ currentUser }}</span>
        <a-button type="primary" @click="downloadPPTX">
          <template #icon><DownloadOutlined /></template>
          下载PPTX
        </a-button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="presenter-main">
      <!-- Left: Thumbnail List -->
      <div class="thumbnail-panel">
        <div class="thumbnail-list">
          <div
            v-for="(slide, idx) in slides"
            :key="idx"
            class="thumbnail-item"
            :class="{ active: idx === currentPage }"
            @click="goToPage(idx)"
          >
            <div class="thumbnail-number">{{ idx + 1 }}</div>
            <div class="thumbnail-preview" :style="{ background: thumbnailColors[idx % thumbnailColors.length] }">
              <span class="slide-placeholder">{{ idx + 1 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Center: Current Slide -->
      <div class="slide-panel">
        <div class="slide-container" v-if="totalPages > 0">
          <div class="slide-placeholder-main" :style="{ background: thumbnailColors[currentPage % thumbnailColors.length] }">
            <div class="slide-number-large">{{ currentPage + 1 }}</div>
            <div class="slide-label">第 {{ currentPage + 1 }} 页</div>
          </div>
        </div>
        <div v-else class="loading-slide">
          <a-spin size="large" tip="加载中..." />
        </div>
      </div>

      <!-- Right: Notes + Progress -->
      <div class="notes-panel">
        <!-- Progress -->
        <div class="progress-section">
          <div class="progress-label">演示进度</div>
          <a-progress
            :percent="progressPercent"
            :show-info="true"
            :stroke-color="'#1890ff'"
          />
          <div class="progress-detail">{{ currentPage + 1 }} / {{ totalPages }} 页</div>
        </div>

        <!-- Speaker Notes -->
        <div class="notes-section">
          <div class="notes-label">📝 演讲者备注</div>
          <div class="notes-content" v-if="currentNotes">
            {{ currentNotes }}
          </div>
          <div class="notes-empty" v-else>
            <span v-if="loadingNotes">加载中...</span>
            <span v-else>暂无备注</span>
          </div>
        </div>

        <!-- Navigation Controls -->
        <div class="nav-section">
          <a-button-group>
            <a-button @click="prevPage" :disabled="currentPage === 0">
              <template #icon><LeftOutlined /></template>
              上一页
            </a-button>
            <a-button @click="nextPage" :disabled="currentPage >= totalPages - 1">
              下一页
              <template #icon><RightOutlined /></template>
            </a-button>
          </a-button-group>
          <div class="keyboard-hint">
            <span>⌨️ 键盘: ← → 翻页 | 空格 下一页</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownloadOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons-vue'

const API = 'http://localhost:8000/api'

const route = useRoute()
const filename = computed(() => route.params.filename || '')
const currentPage = ref(0)
const totalPages = ref(0)
const slides = ref([])
const loadingNotes = ref(false)
const currentUser = ref('')

// Thumbnail colors palette
const thumbnailColors = [
  'linear-gradient(135deg, #667eea, #764ba2)',
  'linear-gradient(135deg, #f093fb, #f5576c)',
  'linear-gradient(135deg, #4facfe, #00f2fe)',
  'linear-gradient(135deg, #43e97b, #38f9d7)',
  'linear-gradient(135deg, #fa709a, #fee140)',
  'linear-gradient(135deg, #a8edea, #fed6e3)',
  'linear-gradient(135deg, #d299c2, #fef9d7)',
  'linear-gradient(135deg, #89f7fe, #66a6ff)',
  'linear-gradient(135deg, #cd9cf2, #f6f3ff)',
  'linear-gradient(135deg, #e0c3fc, #8ec5fc)',
]

const progressPercent = computed(() => {
  if (totalPages.value === 0) return 0
  return Math.round(((currentPage.value + 1) / totalPages.value) * 100)
})

const currentNotes = computed(() => {
  if (slides.value.length > 0 && slides.value[currentPage.value]) {
    return slides.value[currentPage.value].notes || ''
  }
  return ''
})

// Load current user from localStorage
function loadCurrentUser() {
  try {
    const userStr = localStorage.getItem('demoppt_user')
    if (userStr) {
      const user = JSON.parse(userStr)
      currentUser.value = user.username || user.name || user.email || ''
    }
    // Fallback to token-based user info
    if (!currentUser.value) {
      const token = localStorage.getItem('demoppt_token')
      if (token) {
        currentUser.value = '已登录用户'
      }
    }
  } catch (e) {
    console.warn('读取用户信息失败:', e)
  }
}

// Load PPT slides info
async function loadSlides() {
  if (!filename.value) {
    message.error('未指定文件名')
    return
  }

  try {
    const resp = await fetch(`${API}/ppt/${filename.value}/slides`)
    const data = await resp.json()

    if (data.success) {
      totalPages.value = data.slide_count
      slides.value = data.slides
    } else {
      message.error('加载PPT信息失败')
    }
  } catch (e) {
    message.error('加载PPT信息失败: ' + e.message)
  }
}

// Navigation functions
function goToPage(idx) {
  if (idx >= 0 && idx < totalPages.value) {
    currentPage.value = idx
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
  }
}

function prevPage() {
  if (currentPage.value > 0) {
    currentPage.value--
  }
}

// Download PPTX
function downloadPPTX() {
  if (filename.value) {
    window.open(`${API}/download/${filename.value}`, '_blank')
  }
}

// Keyboard navigation
function handleKeydown(e) {
  switch (e.key) {
    case 'ArrowRight':
    case ' ':
      e.preventDefault()
      nextPage()
      break
    case 'ArrowLeft':
      e.preventDefault()
      prevPage()
      break
    case 'Home':
      e.preventDefault()
      goToPage(0)
      break
    case 'End':
      e.preventDefault()
      goToPage(totalPages.value - 1)
      break
  }
}

onMounted(() => {
  loadCurrentUser()
  loadSlides()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.presenter-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a2e;
  color: #fff;
}

.presenter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #16213e;
  border-bottom: 1px solid #2d3a5c;
}

.header-left,
.header-center,
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filename {
  font-size: 14px;
  color: #a0a0a0;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-indicator {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.user-info {
  font-size: 14px;
  color: #a0a0a0;
}

.presenter-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Left: Thumbnail Panel */
.thumbnail-panel {
  width: 180px;
  background: #16213e;
  border-right: 1px solid #2d3a5c;
  overflow-y: auto;
  padding: 16px 8px;
}

.thumbnail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.thumbnail-item {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
  border: 2px solid transparent;
  background: #1a1a2e;
}

.thumbnail-item:hover {
  transform: scale(1.02);
  border-color: #4a5568;
}

.thumbnail-item.active {
  border-color: #1890ff;
  box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
}

.thumbnail-number {
  padding: 4px 8px;
  font-size: 12px;
  color: #a0a0a0;
  background: #0f0f1a;
}

.thumbnail-preview {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slide-placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-size: 18px;
  font-weight: bold;
}

/* Center: Slide Panel */
.slide-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #0f0f1a;
}

.slide-container {
  width: 100%;
  max-width: 900px;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.slide-placeholder-main {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.slide-number-large {
  font-size: 120px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.3);
}

.slide-label {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: -20px;
}

.loading-slide {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* Right: Notes Panel */
.notes-panel {
  width: 320px;
  background: #16213e;
  border-left: 1px solid #2d3a5c;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 24px;
}

.progress-section {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 16px;
}

.progress-label {
  font-size: 14px;
  color: #a0a0a0;
  margin-bottom: 12px;
}

.progress-detail {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  color: #a0a0a0;
}

.notes-section {
  flex: 1;
  background: #1a1a2e;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notes-label {
  font-size: 14px;
  color: #a0a0a0;
  margin-bottom: 12px;
}

.notes-content {
  flex: 1;
  font-size: 15px;
  line-height: 1.8;
  color: #e0e0e0;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.notes-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
}

.nav-section {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-section :deep(.ant-btn-group) {
  width: 100%;
}

.nav-section :deep(.ant-btn) {
  flex: 1;
}

.keyboard-hint {
  text-align: center;
  font-size: 12px;
  color: #666;
}
</style>
