<template>
  <div class="page-container">
    <a-card :bordered="false" class="settings-card">
      <template #title>
        <span class="page-title">模型配置</span>
      </template>
      <template #extra>
        <a-button type="link" @click="showAddForm = !showAddForm">
          {{ showAddForm ? '收起' : '添加配置' }}
        </a-button>
      </template>
      
      <p class="desc">添加您的AI模型API配置，生成的PPT将使用您选择的模型</p>

      <!-- Add Form -->
      <a-collapse v-if="showAddForm" :bordered="false" class="add-form-collapse">
        <a-collapse-panel key="1" header="添加模型配置">
          <a-form 
            :model="form" 
            layout="vertical"
            class="model-form">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="配置名称">
                  <a-input v-model:value="form.name" placeholder="如：我的GPT-4" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="服务商">
                  <a-select v-model:value="form.provider">
                    <a-select-option value="openai">OpenAI (GPT)</a-select-option>
                    <a-select-option value="anthropic">Anthropic (Claude)</a-select-option>
                    <a-select-option value="deepseek">DeepSeek</a-select-option>
                    <a-select-option value="ollama">🖥️ Ollama 本地</a-select-option>
                    <a-select-option value="lmstudio">🖥️ LM Studio 本地</a-select-option>
                    <a-select-option value="jan">🖥️ Jan 本地</a-select-option>
                    <a-select-option value="localai">🖥️ LocalAI 本地</a-select-option>
                    <a-select-option value="custom">🔧 自定义API</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-form-item label="API地址">
              <a-input v-model:value="form.api_base" placeholder="https://api.openai.com/v1" />
            </a-form-item>
            
            <a-form-item label="API Key">
              <a-input-password v-model:value="form.api_key" placeholder="sk-xxxxxx" />
            </a-form-item>
            
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="模型名称">
                  <a-auto-complete 
                    v-model:value="form.model_name" 
                    :options="localModels.map(m => ({ value: m.name || m.id }))"
                    placeholder="gpt-4"
                    class="model-autocomplete">
                    <template #option="item">
                      {{ item.value }}
                    </template>
                  </a-auto-complete>
                  <span v-if="['ollama','lmstudio','jan'].includes(form.provider)" class="hint">
                    点击📥获取本地已安装的模型
                  </span>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label=" " :colon="false">
                  <a-checkbox v-model:checked="form.is_default">设为默认</a-checkbox>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item>
              <a-space>
                <a-button @click="testConfig" :loading="testing">
                  {{ testing ? '测试中...' : '测试连接' }}
                </a-button>
                <a-button type="primary" @click="addModel" :loading="saving">
                  {{ saving ? '保存中...' : '保存配置' }}
                </a-button>
              </a-space>
            </a-form-item>

            <!-- Test Result -->
            <a-alert
              v-if="testResult"
              :type="testResult.success ? 'success' : 'error'"
              :message="testResult.success ? '✓ ' + testResult.message : '✗ ' + testResult.error"
              :description="testResult.response"
              show-icon
            />
          </a-form>
        </a-collapse-panel>
      </a-collapse>

      <!-- Configs List -->
      <a-divider>已配置模型</a-divider>
      
      <a-empty v-if="configs.length === 0" description="暂无配置，请添加" />
      
      <a-list
        v-else
        :data-source="configs"
        item-layout="horizontal"
        :pagination="{ pageSize: 5 }"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <template #actions>
              <a-button 
                v-if="!item.is_default" 
                type="link" 
                size="small"
                @click="setDefault(item.id)">
                设为默认
              </a-button>
              <a-popconfirm
                title="确定删除此配置？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="deleteModel(item.id)"
              >
                <a-button type="link" danger size="small">删除</a-button>
              </a-popconfirm>
            </template>
            <a-list-item-meta>
              <template #title>
                <a-space>
                  <span class="config-name">{{ item.name }}</span>
                  <a-tag :color="getProviderColor(item.provider)">{{ item.provider }}</a-tag>
                  <a-tag v-if="item.is_default" color="blue">默认</a-tag>
                </a-space>
              </template>
              <template #description>
                <div class="config-details">
                  <div><span class="label">API地址：</span><span class="value">{{ item.api_base }}</span></div>
                  <div><span class="label">API Key：</span><span class="value">{{ item.api_key }}</span></div>
                  <div><span class="label">模型：</span><span class="value">{{ item.model_name }}</span></div>
                </div>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- Message Toast -->
    <a-alert
      v-if="message"
      :class="['message-toast', success ? 'success' : 'error']"
      :message="message"
      closable
      @close="message = ''"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const API_BASE = 'http://localhost:8000'

const form = ref({
  name: '',
  provider: 'openai',
  api_base: 'https://api.openai.com/v1',
  api_key: '',
  model_name: 'gpt-4',
  is_default: false
})

const configs = ref([])
const testing = ref(false)
const saving = ref(false)
const testResult = ref(null)
const message = ref('')
const success = ref(true)
const localModels = ref([])
const fetchingModels = ref(false)
const showAddForm = ref(true)

// provider切换时自动填充默认值
watch(() => form.value.provider, (newProvider) => {
  const localDefaults = {
    ollama: { api_base: 'http://localhost:11434/v1', model_name: 'llama3.2' },
    lmstudio: { api_base: 'http://localhost:1234/v1', model_name: '' },
    jan: { api_base: 'http://localhost:1337/v1', model_name: '' },
    localai: { api_base: 'http://localhost:8080/v1', model_name: '' },
  }
  if (localDefaults[newProvider]) {
    form.value.api_base = localDefaults[newProvider].api_base
    form.value.api_key = localDefaults[newProvider].api_key || 'local'
    form.value.model_name = localDefaults[newProvider].model_name
  } else if (newProvider === 'deepseek') {
    form.value.api_base = 'https://api.deepseek.com/v1'
    form.value.api_key = ''
    form.value.model_name = 'deepseek-chat'
  } else if (newProvider === 'anthropic') {
    form.value.api_base = 'https://api.anthropic.com/v1'
    form.value.api_key = ''
    form.value.model_name = 'claude-3-5-sonnet-latest'
  } else {
    form.value.api_base = 'https://api.openai.com/v1'
    form.value.api_key = ''
    form.value.model_name = 'gpt-4o-mini'
  }
})

async function fetchLocalModels() {
  const endpoints = {
    ollama: 'http://localhost:11434/api/tags',
    lmstudio: 'http://localhost:1234/v1/models',
    jan: 'http://localhost:1337/v1/models',
  }
  const endpoint = endpoints[form.value.provider]
  if (!endpoint) return
  fetchingModels.value = true
  localModels.value = []
  try {
    const res = await fetch(endpoint)
    if (res.ok) {
      const data = await res.json()
      if (form.value.provider === 'ollama') {
        localModels.value = data.models || []
      } else {
        localModels.value = (data.data || []).map(m => ({ name: m.id || m.name }))
      }
      if (localModels.value.length === 0) {
        showMsg('未检测到本地模型，请确认服务已启动', false)
      } else {
        showMsg(`已获取${localModels.value.length}个本地模型`, true)
        form.value.model_name = localModels.value[0].name || localModels.value[0].id || ''
      }
    } else {
      showMsg(`连接失败(${res.status})，请确认服务已启动`, false)
    }
  } catch (e) {
    showMsg('本地服务未运行或无法连接，请确认Ollama/LM Studio/Jan已启动', false)
  } finally {
    fetchingModels.value = false
  }
}

function getHeaders() {
  const token = localStorage.getItem('demoppt_token')
  return { 'Authorization': `Bearer ${token}` }
}

onMounted(() => {
  loadConfigs()
})

async function loadConfigs() {
  try {
    const res = await fetch(`${API_BASE}/api/models`, { headers: getHeaders() })
    const data = await res.json()
    if (data.success) {
      configs.value = data.configs || []
    }
  } catch (e) {
    showMsg('加载配置失败', false)
  }
}

async function testConfig() {
  testing.value = true
  testResult.value = null
  try {
    const res = await fetch(`${API_BASE}/api/models/test?api_base=${encodeURIComponent(form.value.api_base)}&api_key=${form.value.api_key}&model_name=${form.value.model_name}&provider=${form.value.provider}`, {
      method: 'POST'
    })
    const data = await res.json()
    testResult.value = data
  } catch (e) {
    testResult.value = { success: false, error: '网络错误' }
  } finally {
    testing.value = false
  }
}

async function addModel() {
  if (!form.value.name || !form.value.api_base || !form.value.api_key || !form.value.model_name) {
    showMsg('请填写完整信息', false)
    return
  }
  
  saving.value = true
  try {
    const res = await fetch(`${API_BASE}/api/models`, {
      method: 'POST',
      headers: { ...getHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        name: form.value.name, 
        api_base: form.value.api_base, 
        api_key: form.value.api_key, 
        model_name: form.value.model_name, 
        provider: form.value.provider, 
        is_default: form.value.is_default ? 1 : 0 
      })
    })
    const data = await res.json()
    
    if (data.success) {
      showMsg('添加成功', true)
      form.value = { name: '', provider: 'openai', api_base: 'https://api.openai.com/v1', api_key: '', model_name: 'gpt-4', is_default: false }
      testResult.value = null
      loadConfigs()
    } else {
      showMsg(data.error || '添加失败', false)
    }
  } catch (e) {
    showMsg('网络错误', false)
  } finally {
    saving.value = false
  }
}

async function setDefault(id) {
  await fetch(`${API_BASE}/api/models/${id}/default`, {
    method: 'POST',
    headers: getHeaders()
  })
  loadConfigs()
}

async function deleteModel(id) {
  await fetch(`${API_BASE}/api/models/${id}`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  loadConfigs()
}

function showMsg(msg, ok) {
  message.value = msg
  success.value = ok
  setTimeout(() => message.value = '', 3000)
}

function getProviderColor(provider) {
  const colors = {
    openai: 'green',
    anthropic: 'orange',
    deepseek: 'blue',
    ollama: 'purple',
    lmstudio: 'cyan',
    jan: 'magenta',
    localai: 'default',
    custom: 'default'
  }
  return colors[provider] || 'default'
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.settings-card {
  border-radius: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.desc {
  color: #8c8c8c;
  margin-bottom: 24px;
}

.add-form-collapse {
  margin-bottom: 24px;
}

.model-form :deep(.ant-form-item) {
  margin-bottom: 16px;
}

.hint {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
  display: block;
}

.config-name {
  font-weight: 600;
  font-size: 15px;
}

.config-details {
  font-size: 13px;
}

.config-details .label {
  color: #8c8c8c;
}

.config-details .value {
  color: #262626;
  font-family: monospace;
}

.message-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  max-width: 400px;
}

.message-toast.success {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.message-toast.error {
  background: #fff2f0;
  border-color: #ffccc7;
}
</style>
