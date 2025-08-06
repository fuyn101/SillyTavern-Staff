<template>
  <div>
    <n-button @click="showDrawer = true" type="primary">预览 JSON 数据</n-button>
    <n-drawer v-model:show="showDrawer" :width="502">
      <n-drawer-content title="JSON 数据预览" closable>
        <div class="json-content">
          <pre>{{ jsonData }}</pre>
        </div>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps({
  jsonData: {
    type: String,
    required: true
  }
})

const showDrawer = ref(false)
</script>

<style scoped>
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
