<template>
  <div class="file-manager-container">
    <n-h1>文件管理器</n-h1>
    <n-space style="margin-bottom: 24px;">
      <input type="file" @change="handleFileUpload" accept="image/png" />
    </n-space>
    <n-list bordered>
      <n-list-item v-for="card in cardList" :key="card.name">
        <div class="card-layout">
          <img :src="card.avatar_data_url" v-if="card.avatar_data_url" class="side-avatar">
          <n-card :title="card.name" class="card-content">
            <p>{{ card.description }}</p>
            <template #action>
              <n-space>
                <n-button @click="loadCard(card.name)">加载</n-button>
                <n-button type="error" @click="deleteCard(card.name)">删除</n-button>
              </n-space>
            </template>
          </n-card>
        </div>
      </n-list-item>
    </n-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useDataManager, type CharacterData } from '@/utils/dataManager'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'

const dataManager = useDataManager()
const router = useRouter()
const message = useMessage()
const cardList = ref<CharacterData[]>([])

const refreshList = () => {
  cardList.value = dataManager.getCardList()
}

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
            dataManager.saveCardToList(cardData as any)
            refreshList()
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

const extractDataFromPng = (arrayBuffer: ArrayBuffer): object | null => {
  const view = new DataView(arrayBuffer)
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

    offset += 12 + length
  }

  return null
}

const loadCard = (name: string) => {
  if (dataManager.loadCardFromList(name)) {
    message.success(`已加载角色卡: ${name}`)
    router.push('/editor') // 跳转到编辑器
  } else {
    message.error('加载失败！')
  }
}

const deleteCard = (name: string) => {
  dataManager.deleteCardFromList(name)
  message.success(`已删除角色卡: ${name}`)
  refreshList()
}

onMounted(() => {
  refreshList()
})
</script>

<style scoped>
.file-manager-container {
  padding: 24px;
}
.card-layout {
  display: flex;
  align-items: flex-start;
}
.side-avatar {
  width: 128px; /* 512/4 */
  height: 192px; /* 768/4 */
  object-fit: cover;
  margin-right: 24px;
  border-radius: 4px;
}
.card-content {
  flex: 1;
}
</style>
