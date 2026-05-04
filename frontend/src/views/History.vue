<template>
  <div class="page-container">
    <a-card :bordered="false" class="history-card">
      <template #title>
        <span class="page-title">我的PPT历史</span>
      </template>
      
      <!-- Loading State -->
      <a-spin v-if="loading" tip="加载中...">
        <div class="loading-placeholder"></div>
      </a-spin>
      
      <!-- Empty State -->
      <a-result
        v-else-if="records.length === 0"
        status="info"
        title="暂无历史记录"
        sub-title="快去创建一个PPT吧！"
      >
        <template #extra>
          <router-link to="/create">
            <a-button type="primary">去创建一个</a-button>
          </router-link>
        </template>
      </a-result>
      
      <!-- History List -->
      <a-list
        v-else
        :data-source="records"
        item-layout="horizontal"
        :pagination="{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
        }"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <template #actions>
              <a v-if="item.url" :href="item.url" download target="_blank">
                <a-button type="link" size="small">下载</a-button>
              </a>
              <a-button type="link" danger size="small" @click="deleteRecord(item.id)">删除</a-button>
            </template>
            <a-list-item-meta>
              <template #title>
                <span class="history-topic">{{ item.topic }}</span>
              </template>
              <template #description>
                <span class="history-meta">
                  {{ item.date }} · {{ item.industry || '通用' }} · {{ formatSize(item.file_size) }}
                </span>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'

const API = 'http://localhost:8000/api'
const records = ref([])
const loading = ref(true)

onMounted(() => {
  loadHistory()
})

async function loadHistory() {
  loading.value = true
  try {
    const resp = await fetch(`${API}/history`)
    const data = await resp.json()
    if (data.success) {
      records.value = data.records || []
    }
  } catch (e) {
    message.error('加载历史记录失败')
  }
  loading.value = false
}

async function deleteRecord(id) {
  Modal.confirm({
    title: '确定删除这条记录？',
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      await fetch(`${API}/history/${id}`, { method: 'DELETE' })
      message.success('删除成功')
      loadHistory()
    }
  })
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.history-card {
  border-radius: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.loading-placeholder {
  height: 200px;
}

.history-topic {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.history-meta {
  font-size: 13px;
  color: #8c8c8c;
}
</style>
