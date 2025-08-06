<template>
  <n-layout has-sider>
    <n-layout-sider width="70%" bordered>
      <n-layout>
        <n-layout-header>
          <n-h1>编辑器</n-h1>
        </n-layout-header>
        <n-layout-content content-style="padding: 24px;">
          <n-tabs type="line" animated @update:value="handleTabChange">
            <!-- 第一个标签页：编辑林凰.json -->
            <n-tab-pane name="BasicContent" tab="编辑基础内容">
              <CharacterBasicEditor ref="basicContentEditorRef" />
            </n-tab-pane>

            <!-- 第二个标签页：编辑data -->
            <n-tab-pane name="data" tab="编辑data">
              <CharacterDataEditor ref="dataEditorRef" />
            </n-tab-pane>
          </n-tabs>
        </n-layout-content>
      </n-layout>
    </n-layout-sider>

    <JsonPreviewContent :jsonData="jsonData" @data-changed="handleDataChange" />
  </n-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import CharacterBasicEditor from '@/components/char/CharacterBasicEditor.vue'
import CharacterDataEditor from '@/components/char/CharacterDataEditor.vue'
import JsonPreviewContent from '@/components/char/JsonPreviewContent.vue'
import { useDataManager } from '@/utils/dataManager'
import { useMessage } from 'naive-ui'

const dataManager = useDataManager()
const jsonData = ref<string>('')
const basicContentEditorRef = ref<InstanceType<typeof CharacterBasicEditor> | null>(null)
const dataEditorRef = ref<InstanceType<typeof CharacterDataEditor> | null>(null)
const activeTab = ref<string>('BasicContent')

// 处理标签页切换
const handleTabChange = (name: string | number) => {
  activeTab.value = name as string
}

// 处理数据变化
const handleDataChange = () => {
  updateJsonDisplay()
}

// 更新JSON显示
const updateJsonDisplay = () => {
  try {
    jsonData.value = JSON.stringify(dataManager.getFullData(), null, 2)
  } catch (error) {
    jsonData.value = 'JSON数据加载失败'
    console.error('JSON数据加载失败:', error)
  }
}

// 监听数据变化
onMounted(() => {
  updateJsonDisplay()

  // 监听自定义数据变化事件
  const handleDataChange = () => {
    updateJsonDisplay()
  }

  // 监听char-data-changed事件
  window.addEventListener('char-data-changed', handleDataChange)

  // 组件卸载时移除监听器
  onUnmounted(() => {
    window.removeEventListener('char-data-changed', handleDataChange)
  })
})
</script>

<style scoped>
.n-layout-sider {
  background-color: var(--secondary-bg-color);
}

.n-layout {
  height: 100vh;
}

.n-layout-header {
  height: 64px;
  line-height: 64px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  background-color: var(--n-color);
  border-bottom: 1px solid var(--n-border-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.n-tabs {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>
