<template>
  <n-layout-content content-style="padding: 0; height: 100%;">
    <div class="json-preview">
      <div class="json-header">
        <h3>JSON 数据预览</h3>
      </div>
      <div class="json-content">
        <pre>{{ jsonData }}</pre>
      </div>
    </div>
  </n-layout-content>
</template>

<script setup lang="ts">
import { useDataManager } from '@/store/dataManager'

defineProps({
  jsonData: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['data-changed'])

const dataManager = useDataManager()
</script>

<style scoped>
.json-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--tertiary-bg-color);
}

.json-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.json-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.button-group {
  display: flex;
  gap: 8px;
}

.json-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.json-content pre {
  margin: 0;
  font-family: var(--font-family-mono);
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: var(--primary-text-color);
}
</style>
