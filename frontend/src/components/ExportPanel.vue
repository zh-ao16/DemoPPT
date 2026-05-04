<template>
  <div class="export-panel">
    <!-- Format Selection -->
    <div class="export-panel__section">
      <h3 class="export-panel__title">导出格式</h3>
      <div class="export-panel__formats">
        <button
          v-for="format in formats"
          :key="format.id"
          class="export-panel__format"
          :class="{ 'export-panel__format--selected': selectedFormat === format.id }"
          @click="selectedFormat = format.id"
        >
          <div class="export-panel__format-icon" :style="{ background: format.color }">
            <svg v-if="format.id === 'pptx'" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 1.5L18.5 9H13V3.5zM9.5 16.5c0-.83.67-1.5 1.5-1.5h2c.83 0 1.5.67 1.5 1.5v1c0 .83-.67 1.5-1.5 1.5h-2c-.83 0-1.5-.67-1.5-1.5v-1zm0-4c0-.83.67-1.5 1.5-1.5h4c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-4c-.83 0-1.5-.67-1.5-1.5zm8.5 4c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5z"/>
            </svg>
            <svg v-else-if="format.id === 'pdf'" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
            </svg>
          </div>
          <span class="export-panel__format-name">{{ format.label }}</span>
          <span class="export-panel__format-ext">.{{ format.id }}</span>
        </button>
      </div>
    </div>

    <!-- Export Options -->
    <div class="export-panel__section">
      <h3 class="export-panel__title">导出设置</h3>
      <div class="export-panel__options">
        <label
          v-for="option in exportOptions"
          :key="option.id"
          class="export-panel__option"
        >
          <input
            type="checkbox"
            v-model="selectedOptions"
            :value="option.id"
            class="export-panel__checkbox"
          />
          <span class="export-panel__checkbox-custom"></span>
          <span class="export-panel__option-label">{{ option.label }}</span>
          <span v-if="option.recommended" class="export-panel__option-tag">推荐</span>
        </label>
      </div>
    </div>

    <!-- Page Range -->
    <div class="export-panel__section">
      <h3 class="export-panel__title">页面范围</h3>
      <div class="export-panel__range">
        <button
          v-for="range in pageRanges"
          :key="range.id"
          class="export-panel__range-btn"
          :class="{ 'export-panel__range-btn--selected': selectedRange === range.id }"
          @click="selectedRange = range.id"
        >
          {{ range.label }}
        </button>
      </div>
    </div>

    <!-- Export Preview -->
    <div class="export-panel__preview">
      <h3 class="export-panel__title">导出预览</h3>
      <div class="export-panel__preview-box">
        <div class="export-panel__preview-row">
          <span class="export-panel__preview-label">文件名:</span>
          <span class="export-panel__preview-value">{{ fileName }}</span>
        </div>
        <div class="export-panel__preview-row">
          <span class="export-panel__preview-label">格式:</span>
          <span class="export-panel__preview-value">{{ selectedFormatLabel }}</span>
        </div>
        <div class="export-panel__preview-row">
          <span class="export-panel__preview-label">大小:</span>
          <span class="export-panel__preview-value">约 {{ estimatedSize }}</span>
        </div>
        <div class="export-panel__preview-row">
          <span class="export-panel__preview-label">页数:</span>
          <span class="export-panel__preview-value">{{ totalPages }} 页</span>
        </div>
      </div>
    </div>

    <!-- Export Progress -->
    <div v-if="exportStatus === 'exporting'" class="export-panel__progress">
      <div class="export-panel__progress-header">
        <span>正在导出...</span>
        <span class="export-panel__progress-percent">{{ exportProgress }}%</span>
      </div>
      <div class="export-panel__progress-bar">
        <div
          class="export-panel__progress-fill"
          :style="{ width: `${exportProgress}%` }"
        ></div>
      </div>
      <p class="export-panel__progress-detail">{{ currentExportStep }}</p>
      <button class="export-panel__cancel-btn" @click="$emit('cancel')">取消导出</button>
    </div>

    <!-- Export Result -->
    <div v-if="exportStatus === 'completed'" class="export-panel__result export-panel__result--success">
      <div class="export-panel__result-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </div>
      <h4 class="export-panel__result-title">导出成功！</h4>
      <p class="export-panel__result-path">文件已保存至: {{ savedPath }}</p>
      <div class="export-panel__result-actions">
        <button class="export-panel__btn export-panel__btn--primary" @click="$emit('open')">打开文件</button>
        <button class="export-panel__btn export-panel__btn--secondary" @click="$emit('openFolder')">打开所在文件夹</button>
        <button class="export-panel__btn export-panel__btn--text" @click="$emit('continue')">继续编辑</button>
      </div>
    </div>

    <div v-if="exportStatus === 'failed'" class="export-panel__result export-panel__result--failed">
      <div class="export-panel__result-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
      </div>
      <h4 class="export-panel__result-title">导出失败</h4>
      <p class="export-panel__result-error">原因: {{ errorMessage }}</p>
      <div class="export-panel__result-actions">
        <button class="export-panel__btn export-panel__btn--primary" @click="$emit('retry')">重试</button>
        <button class="export-panel__btn export-panel__btn--text" @click="$emit('contact')">联系客服</button>
        <button class="export-panel__btn export-panel__btn--text" @click="$emit('faq')">常见问题</button>
      </div>
    </div>

    <!-- Export Button -->
    <button
      v-if="exportStatus === 'idle'"
      class="export-panel__submit"
      :disabled="!selectedFormat"
      @click="$emit('export')"
    >
      开始导出
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  fileName?: string
  totalPages?: number
  exportStatus?: 'idle' | 'exporting' | 'completed' | 'failed'
  exportProgress?: number
  currentExportStep?: string
  savedPath?: string
  errorMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  fileName: 'demo_20260504',
  totalPages: 8,
  exportStatus: 'idle',
  exportProgress: 0,
  currentExportStep: '',
  savedPath: '/Downloads/demo_20260504.pptx',
  errorMessage: '格式不兼容'
})

defineEmits<{
  (e: 'export'): void
  (e: 'cancel'): void
  (e: 'retry'): void
  (e: 'contact'): void
  (e: 'faq'): void
  (e: 'open'): void
  (e: 'openFolder'): void
  (e: 'continue'): void
}>()

const formats = [
  { id: 'pptx', label: 'PowerPoint', color: '#D24726' },
  { id: 'pdf', label: 'PDF文档', color: '#EF4444' },
  { id: 'png', label: 'PNG图片', color: '#10B981' },
  { id: 'jpg', label: 'JPG图片', color: '#10B981' }
]

const exportOptions = [
  { id: 'includeFonts', label: '包含字体文件', recommended: true },
  { id: 'compressImages', label: '压缩图片', recommended: false },
  { id: 'addWatermark', label: '添加水印', recommended: false },
  { id: 'singleImage', label: '单张图片导出', recommended: false }
]

const pageRanges = [
  { id: 'all', label: '全部页' },
  { id: 'current', label: '当前页' },
  { id: 'custom', label: '指定页面' }
]

const selectedFormat = ref('pptx')
const selectedOptions = ref<string[]>(['includeFonts'])
const selectedRange = ref('all')

const selectedFormatLabel = computed(() => {
  const format = formats.find(f => f.id === selectedFormat.value)
  return format ? `${format.label} (.${format.id})` : ''
})

const estimatedSize = computed(() => {
  const baseSize = selectedFormat.value === 'pptx' ? 2.3 : 1.8
  const optionMultiplier = selectedOptions.value.includes('compressImages') ? 0.6 : 1
  return `${(baseSize * optionMultiplier).toFixed(1)} MB`
})
</script>

<style scoped>
.export-panel {
  --color-brand: #2563EB;
  --color-brand-light: #DBEAFE;
  --color-brand-dark: #1D4ED8;
  --color-success: #10B981;
  --color-error: #EF4444;
  --color-title: #111827;
  --color-body: #374151;
  --color-secondary: #6B7280;
  --color-placeholder: #9CA3AF;
  --color-border: #E5E7EB;
  --color-bg: #F9FAFB;
  --color-white: #FFFFFF;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

  --font-zh: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
  --font-en: "Inter", "Roboto", system-ui, sans-serif;

  font-family: var(--font-zh);
  background: var(--color-white);
  border-radius: var(--radius-xl);
  padding: 24px;
  max-width: 480px;
}

.export-panel__section {
  margin-bottom: 24px;
}

.export-panel__title {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-title);
  margin: 0 0 16px 0;
}

/* Format Selection */
.export-panel__formats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.export-panel__format {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.export-panel__format:hover {
  background: var(--color-brand-light);
  border-color: var(--color-brand);
}

.export-panel__format--selected {
  background: var(--color-brand);
  border-color: var(--color-brand);
  color: var(--color-white);
}

.export-panel__format-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.export-panel__format-icon svg {
  width: 20px;
  height: 20px;
  color: var(--color-white);
}

.export-panel__format-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-title);
}

.export-panel__format--selected .export-panel__format-name {
  color: var(--color-white);
}

.export-panel__format-ext {
  font-size: 11px;
  color: var(--color-secondary);
  font-family: var(--font-en);
}

.export-panel__format--selected .export-panel__format-ext {
  color: rgba(255,255,255,0.8);
}

/* Options */
.export-panel__options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.export-panel__option {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  position: relative;
}

.export-panel__checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.export-panel__checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.export-panel__checkbox:checked + .export-panel__checkbox-custom {
  background: var(--color-brand);
  border-color: var(--color-brand);
}

.export-panel__checkbox:checked + .export-panel__checkbox-custom::after {
  content: '';
  width: 6px;
  height: 10px;
  border: 2px solid white;
  border-top: none;
  border-left: none;
  transform: rotate(45deg) translate(-1px, -1px);
}

.export-panel__option-label {
  font-size: 15px;
  color: var(--color-body);
}

.export-panel__option-tag {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--color-brand-light);
  color: var(--color-brand);
  border-radius: var(--radius-sm);
  margin-left: auto;
}

/* Page Range */
.export-panel__range {
  display: flex;
  gap: 8px;
}

.export-panel__range-btn {
  flex: 1;
  padding: 10px 16px;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-zh);
  font-size: 14px;
  color: var(--color-body);
  cursor: pointer;
  transition: all 0.15s ease;
}

.export-panel__range-btn:hover {
  border-color: var(--color-brand);
  background: var(--color-brand-light);
}

.export-panel__range-btn--selected {
  background: var(--color-brand);
  border-color: var(--color-brand);
  color: var(--color-white);
}

/* Preview */
.export-panel__preview-box {
  background: var(--color-bg);
  border-radius: var(--radius-md);
  padding: 16px;
}

.export-panel__preview-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.export-panel__preview-row:last-child {
  border-bottom: none;
}

.export-panel__preview-label {
  font-size: 14px;
  color: var(--color-secondary);
}

.export-panel__preview-value {
  font-size: 14px;
  color: var(--color-body);
  font-family: var(--font-en);
}

/* Progress */
.export-panel__progress {
  margin-top: 20px;
  padding: 20px;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
}

.export-panel__progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 15px;
  color: var(--color-body);
}

.export-panel__progress-percent {
  font-family: var(--font-en);
  font-weight: 600;
  color: var(--color-brand);
}

.export-panel__progress-bar {
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: 12px;
}

.export-panel__progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand) 0%, var(--color-brand-dark) 100%);
  border-radius: var(--radius-full);
  transition: width 0.3s linear;
}

.export-panel__progress-detail {
  font-size: 14px;
  color: var(--color-secondary);
  margin: 0 0 12px 0;
}

.export-panel__cancel-btn {
  background: none;
  border: none;
  color: var(--color-secondary);
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  font-family: var(--font-zh);
}

.export-panel__cancel-btn:hover {
  color: var(--color-error);
}

/* Result */
.export-panel__result {
  margin-top: 20px;
  padding: 24px;
  border-radius: var(--radius-lg);
  text-align: center;
}

.export-panel__result--success {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
}

.export-panel__result--failed {
  background: #FEF2F2;
  border: 1px solid #FECACA;
}

.export-panel__result-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.export-panel__result--success .export-panel__result-icon {
  background: var(--color-success);
}

.export-panel__result--failed .export-panel__result-icon {
  background: var(--color-error);
}

.export-panel__result-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.export-panel__result-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.export-panel__result--success .export-panel__result-title {
  color: var(--color-success);
}

.export-panel__result--failed .export-panel__result-title {
  color: var(--color-error);
}

.export-panel__result-path {
  font-size: 14px;
  color: var(--color-body);
  margin: 0 0 20px 0;
  word-break: break-all;
}

.export-panel__result-error {
  font-size: 14px;
  color: var(--color-error);
  margin: 0 0 20px 0;
}

.export-panel__result-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* Buttons */
.export-panel__btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-family: var(--font-zh);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.export-panel__btn--primary {
  background: var(--color-brand);
  color: var(--color-white);
}

.export-panel__btn--primary:hover {
  background: var(--color-brand-dark);
}

.export-panel__btn--secondary {
  background: var(--color-white);
  color: var(--color-brand);
  border: 1px solid var(--color-brand);
}

.export-panel__btn--secondary:hover {
  background: var(--color-brand-light);
}

.export-panel__btn--text {
  background: transparent;
  color: var(--color-secondary);
  text-decoration: underline;
}

.export-panel__btn--text:hover {
  color: var(--color-body);
}

/* Submit Button */
.export-panel__submit {
  width: 100%;
  padding: 14px 24px;
  background: var(--color-brand);
  color: var(--color-white);
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-zh);
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 24px;
}

.export-panel__submit:hover:not(:disabled) {
  background: var(--color-brand-dark);
}

.export-panel__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
