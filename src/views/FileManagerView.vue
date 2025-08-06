<template>
  <div class="file-manager-container">
    <n-h1>文件管理器</n-h1>
    <n-space style="margin-bottom: 24px;">
      <n-button @click="triggerPngImport">导入PNG角色卡</n-button>
      <input type="file" ref="pngUploader" @change="handlePngUpload" accept="image/png" style="display: none;" />
      <n-button @click="triggerJsonImport">导入JSON角色卡</n-button>
      <input type="file" ref="jsonUploader" @change="handleJsonUpload" accept=".json" style="display: none;" multiple />
      <n-button @click="triggerPresetImport">导入预设</n-button>
      <input type="file" ref="presetUploader" @change="handlePresetUpload" accept=".json" style="display: none;" />
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
      <CharacterCardItem
        v-for="card in cardList"
        :key="card.name"
        :card="card"
        :isSelected="selectedCards.includes(card.name)"
        @update:selected="toggleCardSelection"
        @load="loadCard"
        @delete="deleteCard"
      />
    </n-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useDataManager, type CharacterData } from '@/store/dataManager';
import { useMessage, NButton, NSpace, NList, NH1, NPopconfirm } from 'naive-ui';
import { useRouter } from 'vue-router';
import { extractDataFromPng, embedDataInPng } from '@/utils/pngProcessor';
import CharacterCardItem from '@/components/common/CharacterCardItem.vue';

const dataManager = useDataManager();
const router = useRouter();
const message = useMessage();
const cardList = ref<CharacterData[]>([]);
const selectedCards = ref<string[]>([]);
const pngUploader = ref<HTMLInputElement | null>(null);
const jsonUploader = ref<HTMLInputElement | null>(null);
const presetUploader = ref<HTMLInputElement | null>(null);

const refreshList = () => {
  cardList.value = dataManager.getCardList();
  selectedCards.value = [];
};

const handlePngUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const arrayBuffer = e.target?.result as ArrayBuffer;
    if (arrayBuffer) {
      try {
        const cardData = extractDataFromPng(arrayBuffer) as CharacterData | null;
        if (cardData) {
          const fileReaderForDataUrl = new FileReader();
          fileReaderForDataUrl.onload = (e_du) => {
            cardData.avatar_data_url = e_du.target?.result as string;
            dataManager.saveCardToList(cardData);
            refreshList();
            message.success('角色卡导入成功！');
          };
          fileReaderForDataUrl.readAsDataURL(file);
        } else {
          message.error('未在此PNG文件中找到角色卡数据。');
        }
      } catch (error) {
        message.error(`导入失败: ${error instanceof Error ? error.message : '未知错误'}`);
        console.error('导入PNG时出错:', error);
      }
    }
  };
  reader.readAsArrayBuffer(file);
};

const loadCard = (name: string) => {
  if (dataManager.loadCardFromList(name)) {
    message.success(`已加载角色卡: ${name}`);
    router.push('/editor');
  } else {
    message.error('加载失败！');
  }
};

const deleteCard = (name: string) => {
  dataManager.deleteCardFromList(name);
  message.success(`已删除角色卡: ${name}`);
  refreshList();
};

const triggerPngImport = () => {
  pngUploader.value?.click();
};

const triggerJsonImport = () => {
  jsonUploader.value?.click();
};

const triggerPresetImport = () => {
  presetUploader.value?.click();
};

const handleJsonUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (!files) return;

  for (const file of files) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        dataManager.saveCardToList(json);
        message.success(`成功导入 ${file.name}`);
        refreshList();
      } catch (error) {
        message.error(`导入 ${file.name} 失败`);
        console.error(error);
      }
    };
    reader.readAsText(file);
  }
};

const handlePresetUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const preset = JSON.parse(e.target?.result as string);
      // Navigate to the preset editor with the preset data
      router.push({
        name: 'TwoPageEditor',
        state: { presetData: preset },
      });
      message.success(`预设 ${file.name} 已加载，正在跳转到编辑器...`);
    } catch (error) {
      message.error(`导入预设 ${file.name} 失败`);
      console.error(error);
    }
  };
  reader.readAsText(file);
};

const exportSelectedCardsAsJson = () => {
  const cardsToExport = dataManager.getCardsByNames(selectedCards.value);
  if (cardsToExport.length === 0) {
    message.warning('没有选择任何角色卡。');
    return;
  }
  const dataStr = JSON.stringify(cardsToExport.length === 1 ? cardsToExport[0] : cardsToExport, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'selected_cards.json';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  message.success('已导出所选角色卡为JSON');
};

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
      const pngBlob = await embedDataInPng(card, card.avatar_data_url);
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

const deleteSelectedCards = () => {
  dataManager.deleteCardsFromList(selectedCards.value);
  message.success('已删除所选角色卡');
  refreshList();
};

const clearAllCards = () => {
  dataManager.clearAllCards();
  message.success('已清空所有角色卡');
  refreshList();
};

const toggleCardSelection = (name: string, checked: boolean) => {
  if (checked) {
    if (!selectedCards.value.includes(name)) {
      selectedCards.value.push(name);
    }
  } else {
    selectedCards.value = selectedCards.value.filter((cardName) => cardName !== name);
  }
};

onMounted(refreshList);
</script>

<style scoped>
.file-manager-container {
  padding: 24px;
}
</style>
