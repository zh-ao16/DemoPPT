<template>
  <div class="template-hub">
    <div class="hub-header">
      <h2>📚 模板中心</h2>
      <p class="subtitle">免费精品模板，分享赚积分</p>
      <a-button type="primary" size="large" @click="showUpload = true">
        <template #icon>⬆️</template>
        分享模板
      </a-button>
    </div>

    <!-- 标签筛选 -->
    <div class="filter-bar">
      <a-tag
        v-for="tag in allTags"
        :key="tag"
        :color="selectedTag === tag ? 'blue' : 'default'"
        class="tag-item"
        @click="selectedTag = selectedTag === tag ? '' : tag"
      >{{ tag }}</a-tag>
    </div>

    <!-- 模板列表 -->
    <a-spin :spinning="loading">
      <div class="template-grid">
        <div
          v-for="tpl in filteredTemplates"
          :key="tpl.id"
          class="template-card"
          @click="useTemplate(tpl)"
        >
          <div class="card-preview">
            <div class="preview-placeholder">
              <span>{{ tpl.template_name.charAt(0) }}</span>
            </div>
          </div>
          <div class="card-info">
            <h4>{{ tpl.template_name }}</h4>
            <p class="desc">{{ tpl.description || '暂无描述' }}</p>
            <div class="tags">
              <a-tag v-for="tag in (tpl.tags || '').split(',')" :key="tag" size="small">{{ tag }}</a-tag>
            </div>
            <div class="card-footer">
              <span class="author">by 用户{{ tpl.user_id }}</span>
              <a-button type="link" size="small" @click.stop="downloadTemplate(tpl)">下载</a-button>
            </div>
          </div>
        </div>
      </div>

      <a-empty v-if="!loading && filteredTemplates.length === 0" description="暂无模板" />
    </a-spin>

    <!-- 上传弹窗 -->
    <a-modal
      v-model:open="showUpload"
      title="分享模板"
      @ok="handleUpload"
      :confirmLoading="uploading"
    >
      <a-form :form="uploadForm" layout="vertical">
        <a-form-item label="模板名称" name="template_name">
          <a-input v-model:value="uploadForm.template_name" placeholder="如：商务蓝简约风" />
        </a-form-item>
        <a-form-item label="模板描述" name="description">
          <a-textarea v-model:value="uploadForm.description" :rows="3" placeholder="简要描述模板特点..." />
        </a-form-item>
        <a-form-item label="标签（逗号分隔）" name="tags">
          <a-input v-model:value="uploadForm.tags" placeholder="如：商务,简约,蓝色" />
        </a-form-item>
        <a-form-item label="选择文件（.pptx）" name="file">
          <a-upload
            :before-upload="handleFileSelect"
            :file-list="fileList"
            accept=".pptx"
            name="file"
          >
            <a-button>选择文件</a-button>
          </a-upload>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'

const API = 'http://localhost:8000'
const loading = ref(false)
const showUpload = ref(false)
const uploading = ref(false)
const templates = ref([])
const selectedTag = ref('')
const fileList = ref([])
const selectedFile = ref(null)

const uploadForm = ref({
  template_name: '',
  description: '',
  tags: ''
})

const allTags = computed(() => {
  const tags = new Set()
  templates.value.forEach(t => {
    (t.tags || '').split(',').forEach(tag => { if (tag.trim()) tags.add(tag.trim()) })
  })
  return [...tags]
})

const filteredTemplates = computed(() => {
  if (!selectedTag.value) return templates.value
  return templates.value.filter(t =>
    (t.tags || '').split(',').includes(selectedTag.value)
  )
})

onMounted(() => {
  fetchTemplates()
})

async function fetchTemplates() {
  loading.value = true
  try {
    const res = await fetch(`${API}/api/template/public`)
    const data = await res.json()
    if (data.success) {
      templates.value = data.templates || []
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleFileSelect(file) {
  selectedFile.value = file
  fileList.value = [file]
  return false // prevent auto upload
}

async function handleUpload() {
  if (!uploadForm.value.template_name) return message.warning('请填写模板名称')
  if (!selectedFile.value) return message.warning('请选择文件')

  uploading.value = true
  const formData = new FormData()
  formData.append('template_name', uploadForm.value.template_name)
  formData.append('description', uploadForm.value.description)
  formData.append('tags', uploadForm.value.tags)
  formData.append('file', selectedFile.value)

  try {
    const token = localStorage.getItem('demoppt_token')
    const res = await fetch(`${API}/api/template/share`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })
    const data = await res.json()
    if (data.success) {
      message.success('上传成功，等待审核')
      showUpload.value = false
      uploadForm.value = { template_name: '', description: '', tags: '' }
      fileList.value = []
      selectedFile.value = null
    } else {
      message.error(data.error || '上传失败')
    }
  } catch (e) {
    message.error('上传失败')
  } finally {
    uploading.value = false
  }
}

function useTemplate(tpl) {
  // 跳转到创建页，使用该模板
  window.location.href = `/create?template=${encodeURIComponent(tpl.template_file)}`
}

async function downloadTemplate(tpl) {
  window.open(`${API}/api/template/download/${tpl.id}`, '_blank')
}
</script>

<style scoped>
.template-hub { padding: 24px; max-width: 1200px; margin: 0 auto; }
.hub-header { text-align: center; margin-bottom: 24px; }
.hub-header h2 { font-size: 28px; margin-bottom: 4px; }
.subtitle { color: #888; margin-bottom: 16px; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.tag-item { cursor: pointer; }
.template-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.template-card { border: 1px solid #f0f0f0; border-radius: 8px; overflow: hidden; cursor: pointer; transition: box-shadow 0.2s; }
.template-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.card-preview { height: 140px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; }
.preview-placeholder { width: 60px; height: 60px; background: rgba(255,255,255,0.3); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 28px; color: white; font-weight: bold; }
.card-info { padding: 12px; }
.card-info h4 { margin: 0 0 4px; font-size: 15px; }
.desc { font-size: 12px; color: #888; margin: 0 0 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.author { font-size: 11px; color: #aaa; }
</style>
