<template>
  <div
    class="pricing-card"
    :class="{
      'pricing-card--recommended': recommended,
      'pricing-card--selected': selected
    }"
  >
    <!-- Recommended Badge -->
    <div v-if="recommended" class="pricing-card__badge">
      <svg class="pricing-card__badge-star" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
      推荐
    </div>

    <!-- Plan Header -->
    <div class="pricing-card__header">
      <h2 class="pricing-card__name">{{ name }}</h2>
      <div class="pricing-card__price">
        <span class="pricing-card__currency">¥</span>
        <span class="pricing-card__amount">{{ price }}</span>
        <span v-if="price > 0" class="pricing-card__period">/{{ period }}</span>
      </div>
      <p v-if="description" class="pricing-card__description">{{ description }}</p>
    </div>

    <!-- Divider -->
    <div class="pricing-card__divider"></div>

    <!-- Features List -->
    <ul class="pricing-card__features">
      <li
        v-for="feature in features"
        :key="feature.name"
        class="pricing-card__feature"
        :class="{ 'pricing-card__feature--disabled': !feature.included }"
      >
        <svg
          v-if="feature.included"
          class="pricing-card__feature-icon pricing-card__feature-icon--check"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
        </svg>
        <svg
          v-else
          class="pricing-card__feature-icon pricing-card__feature-icon--cross"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
        </svg>
        <span>{{ feature.name }}</span>
      </li>
    </ul>

    <!-- CTA Button -->
    <button
      class="pricing-card__cta"
      :class="ctaClass"
      :disabled="disabled"
      @click="$emit('select')"
    >
      {{ ctaText }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Feature {
  name: string
  included: boolean
}

interface Props {
  name: string
  price: number
  period?: string
  description?: string
  features: Feature[]
  recommended?: boolean
  selected?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  period: '月',
  description: '',
  recommended: false,
  selected: false,
  disabled: false
})

defineEmits<{
  (e: 'select'): void
}>()

const ctaText = computed(() => {
  if (props.name.includes('免费')) return '免费开始'
  if (props.name.includes('企业')) return '联系我们'
  if (props.recommended) return '立即订阅'
  return '选择此套餐'
})

const ctaClass = computed(() => {
  if (props.recommended) return 'pricing-card__cta--primary'
  if (props.name.includes('免费')) return 'pricing-card__cta--secondary'
  if (props.name.includes('企业')) return 'pricing-card__cta--secondary'
  return 'pricing-card__cta--primary'
})
</script>

<style scoped>
.pricing-card {
  --color-brand: #2563EB;
  --color-brand-light: #DBEAFE;
  --color-brand-dark: #1D4ED8;
  --color-success: #10B981;
  --color-warning: #F59E0B;
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
  --shadow-xl: 0 20px 25px rgba(0,0,0,0.15);

  --font-zh: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
  --font-en: "Inter", "Roboto", system-ui, sans-serif;

  position: relative;
  background: var(--color-white);
  border-radius: var(--radius-xl);
  padding: 32px 28px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.pricing-card:hover {
  box-shadow: var(--shadow-lg);
}

.pricing-card--recommended {
  border: 2px solid var(--color-brand);
  transform: scale(1.02);
}

.pricing-card--selected {
  border-color: var(--color-brand);
  box-shadow: 0 0 0 4px var(--color-brand-light);
}

/* Badge */
.pricing-card__badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-brand);
  color: var(--color-white);
  padding: 4px 16px;
  border-radius: var(--radius-full, 9999px);
  font-family: var(--font-zh);
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.pricing-card__badge-star {
  width: 12px;
  height: 12px;
}

/* Header */
.pricing-card__header {
  text-align: center;
  margin-bottom: 24px;
}

.pricing-card__name {
  font-family: var(--font-zh);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-title);
  margin: 0 0 12px 0;
}

.pricing-card__price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  font-family: var(--font-en);
}

.pricing-card__currency {
  font-size: 16px;
  font-weight: 400;
  color: var(--color-body);
  margin-right: 2px;
}

.pricing-card__amount {
  font-size: 40px;
  font-weight: 600;
  color: var(--color-title);
  line-height: 1;
}

.pricing-card__period {
  font-size: 14px;
  font-weight: 400;
  color: var(--color-secondary);
  margin-left: 4px;
}

.pricing-card__description {
  font-family: var(--font-zh);
  font-size: 14px;
  color: var(--color-secondary);
  margin: 8px 0 0 0;
}

/* Divider */
.pricing-card__divider {
  height: 1px;
  background: var(--color-border);
  margin-bottom: 24px;
}

/* Features */
.pricing-card__features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px 0;
  flex: 1;
}

.pricing-card__feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  font-family: var(--font-zh);
  font-size: 15px;
  color: var(--color-body);
}

.pricing-card__feature--disabled {
  color: var(--color-placeholder);
}

.pricing-card__feature-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.pricing-card__feature-icon--check {
  color: var(--color-success);
}

.pricing-card__feature-icon--cross {
  color: var(--color-placeholder);
}

/* CTA Button */
.pricing-card__cta {
  width: 100%;
  padding: 14px 24px;
  border-radius: var(--radius-md);
  font-family: var(--font-zh);
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.pricing-card__cta--primary {
  background: var(--color-brand);
  color: var(--color-white);
  border-color: var(--color-brand);
}

.pricing-card__cta--primary:hover {
  background: var(--color-brand-dark);
  border-color: var(--color-brand-dark);
}

.pricing-card__cta--secondary {
  background: var(--color-white);
  color: var(--color-brand);
  border: 2px solid var(--color-brand);
}

.pricing-card__cta--secondary:hover {
  background: var(--color-brand-light);
}

.pricing-card__cta:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
