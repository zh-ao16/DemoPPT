<template>
  <div class="ai-progress" :class="[`ai-progress--${status}`]">
    <!-- Compact Mode -->
    <template v-if="mode === 'compact'">
      <div class="ai-progress__compact">
        <div class="ai-progress__bar-compact">
          <div
            class="ai-progress__fill-compact"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
        <span class="ai-progress__text-compact">{{ progress }}%</span>
        <span v-if="currentPage" class="ai-progress__page-compact">第{{ currentPage }}页</span>
      </div>
    </template>

    <!-- Full Mode -->
    <template v-else>
      <!-- Status Header -->
      <div class="ai-progress__header">
        <div class="ai-progress__status">
          <svg v-if="status === 'thinking'" class="ai-progress__icon ai-progress__icon--spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="2" stroke-dasharray="31.4 31.4" stroke-linecap="round"/>
          </svg>
          <svg v-else-if="status === 'completed'" class="ai-progress__icon ai-progress__icon--success" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
          </svg>
          <svg v-else-if="status === 'failed'" class="ai-progress__icon ai-progress__icon--error" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <svg v-else class="ai-progress__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <path d="M12 6v6l4 2" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="ai-progress__title">{{ statusText }}</span>
      </div>

      <!-- Main Progress Bar -->
      <div class="ai-progress__bar">
        <div
          class="ai-progress__fill"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>

      <!-- Percentage -->
      <div class="ai-progress__percentage">{{ progress }}%</div>

      <!-- Steps Indicator -->
      <div class="ai-progress__steps">
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="ai-progress__step"
          :class="{
            'ai-progress__step--active': currentStepIndex === index,
            'ai-progress__step--completed': currentStepIndex > index,
            'ai-progress__step--pending': currentStepIndex < index
          }"
        >
          <div class="ai-progress__step-dot">
            <svg v-if="currentStepIndex > index" class="ai-progress__step-check" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
            </svg>
          </div>
          <span class="ai-progress__step-label">{{ step.label }}</span>
        </div>
      </div>

      <!-- Current Step Detail -->
      <div v-if="currentStepDetail" class="ai-progress__detail">
        <span class="ai-progress__detail-label">当前:</span>
        <span class="ai-progress__detail-text">{{ currentStepDetail }}</span>
      </div>

      <!-- Error Message -->
      <div v-if="status === 'failed' && errorMessage" class="ai-progress__error">
        <p class="ai-progress__error-text">{{ errorMessage }}</p>
        <div class="ai-progress__error-actions">
          <button class="ai-progress__btn ai-progress__btn--primary" @click="$emit('retry')">
            重试
          </button>
          <button class="ai-progress__btn ai-progress__btn--text" @click="$emit('contact')">
            联系客服
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Step {
  id: string
  label: string
  progress: [number, number] // [start%, end%]
}

interface Props {
  mode?: 'compact' | 'full'
  status?: 'idle' | 'thinking' | 'generating' | 'completed' | 'failed'
  progress?: number
  currentPage?: number
  totalPages?: number
  currentStepDetail?: string
  errorMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'full',
  status: 'idle',
  progress: 0,
  currentPage: 0,
  totalPages: 0,
  currentStepDetail: '',
  errorMessage: ''
})

defineEmits<{
  (e: 'retry'): void
  (e: 'contact'): void
}>()

const steps: Step[] = [
  { id: 'analyze', label: '分析主题', progress: [0, 10] },
  { id: 'outline', label: '生成大纲', progress: [10, 30] },
  { id: 'content', label: '内容填充', progress: [30, 70] },
  { id: 'layout', label: '智能排版', progress: [70, 85] },
  { id: 'color', label: '配色优化', progress: [85, 95] },
  { id: 'final', label: '最终生成', progress: [95, 100] }
]

const currentStepIndex = computed(() => {
  if (props.status === 'idle' || props.status === 'thinking') return -1
  if (props.status === 'completed') return steps.length - 1
  if (props.status === 'failed') return -1

  for (let i = 0; i < steps.length; i++) {
    const [start, end] = steps[i].progress
    if (props.progress >= start && props.progress < end) {
      return i
    }
  }
  return steps.length - 1
})

const statusText = computed(() => {
  switch (props.status) {
    case 'idle':
      return '等待开始'
    case 'thinking':
      return '正在分析主题...'
    case 'generating':
      return props.currentPage
        ? `正在生成第 ${props.currentPage}/${props.totalPages || '?'} 页...`
        : `正在生成... ${props.progress}%`
    case 'completed':
      return '生成完成！🎉'
    case 'failed':
      return '生成失败'
    default:
      return '处理中...'
  }
})
</script>

<style scoped>
.ai-progress {
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
  --radius-full: 9999px;

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);

  --font-zh: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
  --font-en: "Inter", "SF Pro Display", "Segoe UI", system-ui, sans-serif;

  font-family: var(--font-zh);
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-md);
}

.ai-progress--failed {
  border: 1px solid var(--color-error);
}

.ai-progress--completed {
  border: 1px solid var(--color-success);
}

/* Compact Mode */
.ai-progress__compact {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-progress__bar-compact {
  flex: 1;
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.ai-progress__fill-compact {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand) 0%, var(--color-brand-dark) 100%);
  border-radius: var(--radius-full);
  transition: width 0.3s linear;
}

.ai-progress__text-compact {
  font-family: var(--font-en);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-brand);
  min-width: 40px;
}

.ai-progress__page-compact {
  font-size: 14px;
  color: var(--color-secondary);
}

/* Full Mode */
.ai-progress__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.ai-progress__status {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-progress__icon {
  width: 24px;
  height: 24px;
  color: var(--color-brand);
}

.ai-progress__icon--spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.ai-progress__icon--success {
  color: var(--color-success);
}

.ai-progress__icon--error {
  color: var(--color-error);
}

.ai-progress__title {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-title);
}

/* Progress Bar */
.ai-progress__bar {
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: 12px;
}

.ai-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand) 0%, var(--color-brand-dark) 100%);
  border-radius: var(--radius-full);
  transition: width 0.3s linear;
}

.ai-progress--completed .ai-progress__fill {
  background: var(--color-success);
}

.ai-progress--failed .ai-progress__fill {
  background: var(--color-error);
}

/* Percentage */
.ai-progress__percentage {
  font-family: var(--font-en);
  font-size: 28px;
  font-weight: 600;
  color: var(--color-brand);
  text-align: center;
  margin-bottom: 24px;
}

/* Steps */
.ai-progress__steps {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.ai-progress__step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.ai-progress__step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-border);
  background: var(--color-white);
  transition: all 0.2s ease;
}

.ai-progress__step--completed .ai-progress__step-dot {
  background: var(--color-brand);
  border-color: var(--color-brand);
}

.ai-progress__step--active .ai-progress__step-dot {
  border-color: var(--color-brand);
  background: var(--color-brand);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(37, 99, 235, 0); }
}

.ai-progress__step-check {
  width: 14px;
  height: 14px;
  color: var(--color-white);
}

.ai-progress__step-label {
  font-size: 12px;
  color: var(--color-secondary);
  text-align: center;
}

.ai-progress__step--active .ai-progress__step-label {
  color: var(--color-brand);
  font-weight: 500;
}

.ai-progress__step--completed .ai-progress__step-label {
  color: var(--color-body);
}

/* Detail */
.ai-progress__detail {
  padding: 12px 16px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  font-size: 14px;
}

.ai-progress__detail-label {
  color: var(--color-secondary);
  margin-right: 8px;
}

.ai-progress__detail-text {
  color: var(--color-body);
}

/* Error */
.ai-progress__error {
  margin-top: 16px;
  padding: 16px;
  background: #FEF2F2;
  border-radius: var(--radius-md);
  border: 1px solid #FECACA;
}

.ai-progress__error-text {
  color: var(--color-error);
  font-size: 14px;
  margin: 0 0 16px 0;
}

.ai-progress__error-actions {
  display: flex;
  gap: 12px;
}

.ai-progress__btn {
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-family: var(--font-zh);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.ai-progress__btn--primary {
  background: var(--color-brand);
  color: var(--color-white);
}

.ai-progress__btn--primary:hover {
  background: var(--color-brand-dark);
}

.ai-progress__btn--text {
  background: transparent;
  color: var(--color-secondary);
  text-decoration: underline;
}

.ai-progress__btn--text:hover {
  color: var(--color-body);
}
</style>
