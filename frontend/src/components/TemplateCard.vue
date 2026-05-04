<template>
  <div
    class="template-card"
    :class="{
      'template-card--selected': selected,
      'template-card--disabled': disabled
    }"
    @click="handleClick"
  >
    <!-- Thumbnail Container -->
    <div class="template-card__thumbnail">
      <img
        v-if="thumbnail"
        :src="thumbnail"
        :alt="name"
        class="template-card__image"
      />
      <div v-else class="template-card__placeholder">
        <svg class="template-card__placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="M21 15l-5-5L5 21" />
        </svg>
      </div>

      <!-- Hover Overlay -->
      <div class="template-card__overlay">
        <button class="template-card__btn template-card__btn--preview" @click.stop="$emit('preview')">
          预览
        </button>
        <button class="template-card__btn template-card__btn--use" @click.stop="$emit('use')">
          使用此模板
        </button>
      </div>

      <!-- Selected Badge -->
      <div v-if="selected" class="template-card__badge">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
        </svg>
      </div>
    </div>

    <!-- Card Info -->
    <div class="template-card__info">
      <h3 class="template-card__name">{{ name }}</h3>
      <p class="template-card__scene">{{ scene }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  id: string
  name: string
  scene: string
  thumbnail?: string
  selected?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  thumbnail: '',
  selected: false,
  disabled: false
})

const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'preview'): void
  (e: 'use'): void
}>()

const handleClick = () => {
  emit('select')
}
</script>

<style scoped>
.template-card {
  --color-brand: #2563EB;
  --color-brand-light: #DBEAFE;
  --color-brand-dark: #1D4ED8;
  --color-title: #111827;
  --color-body: #374151;
  --color-secondary: #6B7280;
  --color-border: #E5E7EB;
  --color-white: #FFFFFF;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

  --font-zh: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
  --font-en: "Inter", "SF Pro Display", "Segoe UI", system-ui, sans-serif;

  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.template-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.template-card--selected {
  border-color: var(--color-brand);
}

.template-card--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Thumbnail */
.template-card__thumbnail {
  position: relative;
  width: 100%;
  padding-top: 133.33%; /* 3:4 aspect ratio */
  background: var(--color-border);
  overflow: hidden;
}

.template-card__image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-card__placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-brand-light) 0%, var(--color-white) 100%);
}

.template-card__placeholder-icon {
  width: 48px;
  height: 48px;
  color: var(--color-brand);
  opacity: 0.5;
}

/* Hover Overlay */
.template-card__overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.6) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.template-card:hover .template-card__overlay {
  opacity: 1;
}

.template-card__btn {
  padding: 8px 20px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-family: var(--font-zh);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease-out;
  border: none;
}

.template-card__btn--preview {
  background: var(--color-white);
  color: var(--color-title);
}

.template-card__btn--preview:hover {
  background: var(--color-brand-light);
}

.template-card__btn--use {
  background: var(--color-brand);
  color: var(--color-white);
}

.template-card__btn--use:hover {
  background: var(--color-brand-dark);
}

/* Selected Badge */
.template-card__badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  background: var(--color-brand);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
}

.template-card__badge svg {
  width: 16px;
  height: 16px;
}

/* Card Info */
.template-card__info {
  padding: 16px;
}

.template-card__name {
  font-family: var(--font-zh);
  font-size: 16px;
  font-weight: 500;
  color: var(--color-title);
  margin: 0 0 4px 0;
}

.template-card__scene {
  font-family: var(--font-zh);
  font-size: 14px;
  color: var(--color-secondary);
  margin: 0;
}
</style>
