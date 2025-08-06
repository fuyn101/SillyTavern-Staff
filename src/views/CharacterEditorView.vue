<template>
  <n-layout has-sider>
    <n-layout-sider width="70%" bordered>
      <n-layout>
        <n-layout-header>
          <n-h1>编辑器</n-h1>
          <input type="file" @change="handleFileUpload" accept="image/png" />
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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import CharacterBasicEditor from '@/components/editor/CharacterBasicEditor.vue'
import CharacterDataEditor from '@/components/editor/CharacterDataEditor.vue'
import JsonPreviewContent from '@/components/char/JsonPreviewContent.vue'
import { useDataManager } from '@/store/dataManager'
import { useMessage } from 'naive-ui'

const dataManager = useDataManager()
const jsonData = ref<string>('')
const basicContentEditorRef = ref<InstanceType<typeof CharacterBasicEditor> | null>(null)
const dataEditorRef = ref<InstanceType<typeof CharacterDataEditor> | null>(null)
const activeTab = ref<string>('BasicContent')
const message = useMessage()

// 处理文件上传
const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const arrayBuffer = e.target?.result as ArrayBuffer
    if (arrayBuffer) {
      try {
        const cardData = extractDataFromPng(arrayBuffer)
        if (cardData) {
          const fileReaderForDataUrl = new FileReader();
          fileReaderForDataUrl.onload = (e_du) => {
            const dataUrl = e_du.target?.result as string;
            (cardData as any).avatar_data_url = dataUrl;
            dataManager.setFullData(cardData as any)
            dataManager.saveCardToList(cardData as any)
            updateJsonDisplay()
            message.success('角色卡导入成功！')
          };
          fileReaderForDataUrl.readAsDataURL(file);
        } else {
          message.error('未在此PNG文件中找到角色卡数据。')
        }
      } catch (error) {
        message.error('导入失败，文件可能已损坏或格式不正确。')
        console.error('导入PNG时出错:', error)
      }
    }
  }
  reader.readAsArrayBuffer(file)
}

// 从PNG ArrayBuffer中提取数据
const extractDataFromPng = (arrayBuffer: ArrayBuffer): object | null => {
  const view = new DataView(arrayBuffer)
  // 检查PNG签名
  if (view.getUint32(0) !== 0x89504e47 || view.getUint32(4) !== 0x0d0a1a0a) {
    throw new Error('不是有效的PNG文件。')
  }

  let offset = 8
  while (offset < view.byteLength) {
    const length = view.getUint32(offset)
    const type = String.fromCharCode(
      view.getUint8(offset + 4),
      view.getUint8(offset + 5),
      view.getUint8(offset + 6),
      view.getUint8(offset + 7)
    )

    if (type === 'tEXt') {
      const chunkDataOffset = offset + 8
      const chunkData = new Uint8Array(arrayBuffer, chunkDataOffset, length)
      
      let nullIndex = -1;
      for (let i = 0; i < chunkData.length; i++) {
          if (chunkData[i] === 0) {
              nullIndex = i;
              break;
          }
      }

      if (nullIndex !== -1) {
          const keyDecoder = new TextDecoder('ascii');
          const key = keyDecoder.decode(chunkData.subarray(0, nullIndex));

          if (key === 'ccv3') {
              const base64Data = keyDecoder.decode(chunkData.subarray(nullIndex + 1));
              const binaryString = atob(base64Data);
              const bytes = new Uint8Array(binaryString.length);
              for (let i = 0; i < binaryString.length; i++) {
                  bytes[i] = binaryString.charCodeAt(i);
              }
              
              const utf8Decoder = new TextDecoder('utf-8');
              const jsonString = utf8Decoder.decode(bytes);
              
              return JSON.parse(jsonString);
          }
      }
    }

    offset += 12 + length // 移动到下一个块 (4字节长度 + 4字节类型 + 数据 + 4字节CRC)
  }

  return null
}


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

watch(
  () => dataManager.linhuangData,
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
