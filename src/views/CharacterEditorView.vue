<template>
  <n-layout has-sider>
    <n-layout-sider width="70%" bordered>
      <character-editor />
    </n-layout-sider>
    <JsonPreviewContent :jsonData="jsonData" @data-changed="handleDataChange" />
  </n-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import CharacterEditor from '@/components/editor/CharacterEditor.vue'
import JsonPreviewContent from '@/components/character/CharacterPreview.vue'
import { useDataManager } from '@/store/dataManager'

const dataManager = useDataManager()
const jsonData = ref<string>('')

const handleDataChange = () => {
  updateJsonDisplay()
}

const updateJsonDisplay = () => {
  try {
    jsonData.value = JSON.stringify(dataManager.getFullData(), null, 2)
  } catch (error) {
    jsonData.value = 'JSON数据加载失败'
    console.error('JSON数据加载失败:', error)
  }
}

onMounted(() => {
  updateJsonDisplay()

  const handleDataChange = () => {
    updateJsonDisplay()
  }

  window.addEventListener('char-data-changed', handleDataChange)

  onUnmounted(() => {
    window.removeEventListener('char-data-changed', handleDataChange)
  })
})

watch(
  () => dataManager.characterData,
  () => {
    updateJsonDisplay()
  },
  { deep: true }
)
</script>

<style scoped>
.n-layout-sider {
  background-color: var(--secondary-bg-color);
}
</style>
