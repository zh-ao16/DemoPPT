<template>
  <a-modal
    v-model:open="visible"
    title="🌐 划词翻译"
    width="700px"
    :footer="null"
    @cancel="close"
    class="translator-modal"
  >
    <div class="translator-container">
      <!-- 输入区域 -->
      <div class="input-section">
        <div class="section-header">
          <span class="section-title">📝 输入文本</span>
          <a-space>
            <a-checkbox v-model:checked="batchMode">批量翻译模式</a-checkbox>
            <a-button size="small" @click="loadSelected" v-if="selectedTexts && selectedTexts.length > 0">
              导入已选文本
            </a-button>
          </a-space>
        </div>

        <a-textarea
          v-model:value="inputText"
          :rows="batchMode ? 6 : 4"
          :placeholder="batchMode ? '每行一段文本，支持批量翻译多段\n例如：\n第一段内容\n第二段内容\n第三段内容' : '输入要翻译的文本...'"
          :maxlength="2000"
          showCount
        />
      </div>

      <!-- 设置区域 -->
      <div class="settings-section">
        <div class="setting-item">
          <span class="setting-label">目标语言：</span>
          <a-select v-model:value="targetLang" style="width: 160px">
            <a-select-option value="en">🇺🇸 英文</a-select-option>
            <a-select-option value="ja">🇯🇵 日文</a-select-option>
            <a-select-option value="ko">🇰🇷 韩文</a-select-option>
            <a-select-option value="es">🇪🇸 西班牙文</a-select-option>
            <a-select-option value="fr">🇫🇷 法文</a-select-option>
            <a-select-option value="de">🇩🇪 德文</a-select-option>
          </a-select>
        </div>
        <div class="setting-item">
          <span class="setting-label">语气风格：</span>
          <a-select v-model:value="tone" style="width: 160px">
            <a-select-option value="日常">💬 日常</a-select-option>
            <a-select-option value="正式">🏛️ 正式</a-select-option>
            <a-select-option value="商务">💼 商务</a-select-option>
          </a-select>
        </div>
        <a-button type="primary" @click="doTranslate" :loading="translating" :disabled="!inputText.trim()">
          {{ translating ? '翻译中...' : '🚀 开始翻译' }}
        </a-button>
      </div>

      <!-- 翻译结果 -->
      <div v-if="results.length > 0" class="result-section">
        <div class="section-header">
          <span class="section-title">✨ 翻译结果</span>
          <a-space>
            <a-tag color="blue">{{ langNames[targetLang] }}</a-tag>
            <a-tag>{{ tone }}</a-tag>
            <a-button size="small" @click="copyAll">复制全部</a-button>
            <a-button size="small" type="primary" @click="insertToPPT" v-if="showInsertBtn">插入到PPT</a-button>
          </a-space>
        </div>

        <div class="results-list">
          <div v-for="(item, index) in results" :key="index" class="result-item">
            <div class="result-original">
              <span class="result-label">原文：</span>
              <span class="result-text">{{ item.original }}</span>
            </div>
            <div class="result-translated">
              <span class="result-label">译文：</span>
              <span class="result-text">{{ item.translated }}</span>
            </div>
            <div class="result-actions">
              <a-button size="small" type="link" @click="copyItem(item)">复制</a-button>
              <a-button size="small" type="link" @click="insertOne(item)" v-if="showInsertBtn">插入</a-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <a-empty v-if="!translating && results.length === 0 && hasTranslated" description="未获取到翻译结果" />
    </div>
  </a-modal>
</template>

<script>
const API = 'http://localhost:8000/api'

export default {
  name: 'Translator',
  props: {
    showInsertBtn: {
      type: Boolean,
      default: true
    },
    selectedTexts: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      visible: false,
      inputText: '',
      targetLang: 'en',
      tone: '日常',
      translating: false,
      results: [],
      hasTranslated: false,
      batchMode: false,
      langNames: {
        en: '英文',
        ja: '日文',
        ko: '韩文',
        es: '西班牙文',
        fr: '法文',
        de: '德文'
      }
    }
  },
  methods: {
    open(text = '') {
      this.visible = true
      if (text) {
        this.inputText = text
      }
      this.results = []
      this.hasTranslated = false
    },

    close() {
      this.visible = false
    },

    loadSelected() {
      if (this.selectedTexts && this.selectedTexts.length > 0) {
        this.inputText = this.selectedTexts.join('\n')
        this.batchMode = true
      }
    },

    async doTranslate() {
      if (!this.inputText.trim()) return

      this.translating = true
      this.results = []
      this.hasTranslated = false

      try {
        // 根据批量模式决定如何发送文本
        let texts = []
        if (this.batchMode) {
          // 批量模式：按行分割
          texts = this.inputText.split('\n').filter(t => t.trim())
        } else {
          // 单条模式
          texts = [this.inputText]
        }

        const resp = await fetch(`${API}/translate_text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            texts: texts,
            target_lang: this.targetLang,
            tone: this.tone
          })
        })

        const data = await resp.json()

        if (data.success) {
          this.results = data.translations || []
          this.hasTranslated = true
          this.$message.success(data.message || '翻译成功')
        } else {
          this.$message.error(data.message || '翻译失败')
          this.hasTranslated = true
        }
      } catch (e) {
        this.$message.error('翻译请求失败：' + e.message)
        this.hasTranslated = true
      }

      this.translating = false
    },

    copyItem(item) {
      navigator.clipboard.writeText(item.translated).then(() => {
        this.$message.success('已复制到剪贴板')
      })
    },

    copyAll() {
      const text = this.results.map((item, i) => {
        return `【原文 ${i + 1}】${item.original}\n【译文 ${i + 1}】${item.translated}`
      }).join('\n\n')
      navigator.clipboard.writeText(text).then(() => {
        this.$message.success('已复制全部翻译结果')
      })
    },

    insertOne(item) {
      this.$emit('insert', item.translated)
      this.$message.success('已插入到PPT内容中')
    },

    insertToPPT() {
      if (this.results.length === 0) return

      // 将所有译文组合插入
      const allTranslated = this.results.map(item => item.translated).join('\n\n')
      this.$emit('insert', allTranslated)
      this.$message.success(`已插入${this.results.length}段翻译结果`)
    }
  }
}
</script>

<style scoped>
.translator-modal :deep(.ant-modal-body) {
  padding: 16px;
}

.translator-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.settings-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-label {
  font-size: 13px;
  color: #595959;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
  border-left: 3px solid #1890ff;
}

.result-original {
  margin-bottom: 8px;
}

.result-label {
  font-size: 12px;
  color: #8c8c8c;
  font-weight: 500;
}

.result-text {
  font-size: 14px;
  color: #262626;
  line-height: 1.6;
}

.result-translated {
  padding-left: 8px;
  border-left: 2px solid #52c41a;
}

.result-translated .result-text {
  color: #389e0d;
}

.result-actions {
  margin-top: 8px;
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}
</style>
