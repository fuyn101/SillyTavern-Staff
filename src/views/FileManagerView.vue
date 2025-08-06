<template>
  <div class="file-manager-container">
    <n-h1>文件管理器</n-h1>
    <n-space style="margin-bottom: 24px;">
      <n-button @click="triggerPngImport">导入PNG角色卡</n-button>
      <input type="file" ref="pngUploader" @change="handleFileUpload" accept="image/png" style="display: none;" />
      <n-button @click="triggerJsonImport">导入JSON角色卡</n-button>
      <input type="file" ref="jsonUploader" @change="handleJsonUpload" accept=".json" style="display: none;" multiple />
      <n-button @click="exportSelectedCardsAsJson" :disabled="selectedCards.length === 0">导出为JSON</n-button>
      <n-button @click="exportSelectedCardsAsPng" :disabled="selectedCards.length === 0">导出为PNG</n-button>
      <n-popconfirm @positive-click="deleteSelectedCards">
        <template #trigger>
          <n-button type="error" :disabled="selectedCards.length === 0">删除所选</n-button>
        </template>
        确定要删除所选的 {{ selectedCards.length }} 个角色卡吗？
      </n-popconfirm>
      <n-popconfirm @positive-click="clearAllCards">
        <template #trigger>
          <n-button type="error" danger>清空所有</n-button>
        </template>
        确定要删除所有角色卡吗？此操作不可逆！
      </n-popconfirm>
    </n-space>
    <n-list bordered>
      <n-list-item v-for="card in cardList" :key="card.name">
        <div class="card-layout">
          <n-checkbox :value="card.name" @update:checked="toggleCardSelection(card.name, $event)" style="margin-right: 16px;" />
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
import { useDataManager, type CharacterData } from '@/store/dataManager'
import { useMessage, NButton, NSpace, NList, NListItem, NCard, NH1, NCheckbox, NPopconfirm } from 'naive-ui'
import { useRouter } from 'vue-router'

const dataManager = useDataManager()
const router = useRouter()
const message = useMessage()
const cardList = ref<CharacterData[]>([])
const selectedCards = ref<string[]>([])
const pngUploader = ref<HTMLInputElement | null>(null)
const jsonUploader = ref<HTMLInputElement | null>(null)

const crc32 = (function() {
    const table = new Uint32Array(256);
    for (let i = 0; i < 256; i++) {
        let c = i;
        for (let k = 0; k < 8; k++) {
            c = (c & 1) ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
        }
        table[i] = c;
    }
    return function(bytes: Uint8Array): number {
        let crc = 0xFFFFFFFF;
        for (let i = 0; i < bytes.length; i++) {
            crc = table[(crc ^ bytes[i]) & 0xFF] ^ (crc >>> 8);
        }
        return (crc ^ 0xFFFFFFFF) >>> 0;
    };
})();

const refreshList = () => {
  cardList.value = dataManager.getCardList()
  selectedCards.value = []
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

const triggerPngImport = () => {
  pngUploader.value?.click()
}

const triggerJsonImport = () => {
  jsonUploader.value?.click()
}

const handleJsonUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return

  for (const file of files) {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string)
        dataManager.saveCardToList(json)
        message.success(`成功导入 ${file.name}`)
        refreshList()
      } catch (error) {
        message.error(`导入 ${file.name} 失败`)
        console.error(error)
      }
    }
    reader.readAsText(file)
  }
}

const exportSelectedCardsAsJson = () => {
  const cardsToExport = dataManager.getCardsByNames(selectedCards.value)
  if (cardsToExport.length === 0) {
    message.warning('没有选择任何角色卡。')
    return
  }
  const dataStr = JSON.stringify(cardsToExport.length === 1 ? cardsToExport[0] : cardsToExport, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'selected_cards.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  message.success('已导出所选角色卡为JSON')
}

const exportSelectedCardsAsPng = async () => {
  const cardsToExport = dataManager.getCardsByNames(selectedCards.value);
  if (cardsToExport.length === 0) {
    message.warning('没有选择任何角色卡。');
    return;
  }

  for (const card of cardsToExport) {
    if (!card.avatar_data_url) {
      message.error(`角色卡 "${card.name}" 没有头像，无法导出为PNG。`);
      continue;
    }
    try {
      const pngBlob = await embedDataInPng(card);
      const url = URL.createObjectURL(pngBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${card.name}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      message.success(`已成功导出 "${card.name}" 为PNG文件。`);
    } catch (error) {
      message.error(`导出 "${card.name}" 时出错: ${error}`);
      console.error(error);
    }
  }
};

const embedDataInPng = (card: CharacterData): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        return reject(new Error('无法获取Canvas上下文'));
      }
      ctx.drawImage(img, 0, 0);

      const dataUrl = canvas.toDataURL('image/png');
      
      const cardDataToEmbed = { ...card };
      delete cardDataToEmbed.avatar_data_url;
      const jsonString = JSON.stringify(cardDataToEmbed);
      
      const base64Png = dataUrl.split(',')[1];
      const binaryPng = atob(base64Png);
      const arrayBuffer = new ArrayBuffer(binaryPng.length);
      const uint8Array = new Uint8Array(arrayBuffer);
      for (let i = 0; i < binaryPng.length; i++) {
        uint8Array[i] = binaryPng.charCodeAt(i);
      }

      const dataView = new DataView(uint8Array.buffer);
      let offset = 8;
      let iendOffset = -1;

      while (offset < dataView.byteLength) {
        const length = dataView.getUint32(offset);
        const type = String.fromCharCode(
          dataView.getUint8(offset + 4),
          dataView.getUint8(offset + 5),
          dataView.getUint8(offset + 6),
          dataView.getUint8(offset + 7)
        );
        if (type === 'IEND') {
          iendOffset = offset;
          break;
        }
        offset += 12 + length;
      }

      if (iendOffset === -1) {
        return reject(new Error('无法找到PNG的IEND块'));
      }

      const textEncoder = new TextEncoder();
      const key = 'ccv3';
      const value = btoa(unescape(encodeURIComponent(jsonString)));
      const textChunkData = textEncoder.encode(key + '\0' + value);
      
      const chunkTypeAndData = new Uint8Array(4 + textChunkData.length);
      chunkTypeAndData.set(textEncoder.encode('tEXt'), 0);
      chunkTypeAndData.set(textChunkData, 4);
      
      const crc = crc32(chunkTypeAndData);

      const textChunk = new Uint8Array(12 + textChunkData.length);
      const textChunkView = new DataView(textChunk.buffer);

      textChunkView.setUint32(0, textChunkData.length);
      textChunk.set(chunkTypeAndData, 4);
      textChunkView.setUint32(8 + textChunkData.length, crc);

      const newPngData = new Uint8Array(uint8Array.length + textChunk.length);
      newPngData.set(uint8Array.subarray(0, iendOffset));
      newPngData.set(textChunk, iendOffset);
      newPngData.set(uint8Array.subarray(iendOffset), iendOffset + textChunk.length);

      resolve(new Blob([newPngData], { type: 'image/png' }));
    };
    img.onerror = () => {
      reject(new Error('无法加载角色头像图片。'));
    };
    img.src = card.avatar_data_url!;
  });
};

const deleteSelectedCards = () => {
  dataManager.deleteCardsFromList(selectedCards.value)
  message.success('已删除所选角色卡')
  refreshList()
}

const clearAllCards = () => {
  dataManager.clearAllCards()
  message.success('已清空所有角色卡')
  refreshList()
}

const toggleCardSelection = (name: string, checked: boolean) => {
  if (checked) {
    selectedCards.value.push(name)
  } else {
    selectedCards.value = selectedCards.value.filter(cardName => cardName !== name)
  }
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
