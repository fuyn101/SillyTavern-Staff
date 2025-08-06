<template>
  <n-layout-content content-style="padding: 0; height: 100%;">
    <div class="json-preview">
      <div class="json-header">
        <h3>JSON 数据预览</h3>
        <div class="button-group">
          <n-button size="small" @click="handleImportJson" type="primary">
            导入JSON
          </n-button>
          <n-button size="small" @click="handleExportJson" type="warning">
            导出JSON
          </n-button>
        </div>
      </div>
      <div class="json-content">
        <pre>{{ jsonData }}</pre>
      </div>
    </div>
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useDataManager } from '@/store/dataManager'
import { useMessage } from 'naive-ui'

defineProps({
  jsonData: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['data-changed'])

const dataManager = useDataManager()
const message = useMessage()

// 处理导入JSON
const handleImportJson = () => {
  // 创建文件输入元素
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'

  input.onchange = (event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const jsonContent = e.target?.result as string
        const parsedData = JSON.parse(jsonContent)

        // 使用数据管理器加载JSON数据
        dataManager.loadFromJson(jsonContent)

        // 触发数据变化事件通知父组件
        emit('data-changed')

        message.success('JSON文件导入成功！')
      } catch (error) {
        console.error('JSON文件解析失败:', error)
        message.error('JSON文件解析失败，请检查文件格式')
      }
    }

    reader.readAsText(file)
  }

  // 触发文件选择对话框
  input.click()
}

// 处理导出JSON
const handleExportJson = () => {
  try {
    // 获取当前本地存储的数据
    const savedData = localStorage.getItem('linhuang_full_data')
    if (!savedData) {
      message.warning('本地存储中没有数据可导出')
      return
    }

    // 创建下载链接
    const blob = new Blob([savedData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `linhuang_data_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    // 清空本地存储
    localStorage.removeItem('linhuang_full_data')

    // 重置数据管理器为默认数据
    dataManager.resetToDefault()

    // 触发数据变化事件通知父组件
    emit('data-changed')

    message.success('JSON文件导出成功，本地存储已清空！')
  } catch (error) {
    console.error('导出JSON失败:', error)
    message.error('导出JSON失败')
  }
}
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
