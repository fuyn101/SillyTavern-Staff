<template>
  <n-layout style="height: 100%">
    <n-layout-header bordered class="editor-header">
      <n-h2 >角色卡编辑器</n-h2>
      <n-space>
        <n-dropdown trigger="hover" :options="exportOptions" @select="handleExportSelect">
          <n-button type="primary">导出角色卡</n-button>
        </n-dropdown>
        <n-button @click="showJsonPreview = true">预览 JSON</n-button>
      </n-space>
    </n-layout-header>
    <n-layout-content style="height: calc(100% - 64px); padding: 16px;">
      <CharacterEditor />
    </n-layout-content>
  </n-layout>

  <n-modal
    v-model:show="showJsonPreview"
    preset="card"
    style="width: 600px;"
    title="JSON 数据预览"
  >
    <n-code :code="jsonData" language="json" show-line-numbers />
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { 
  NLayout, 
  NLayoutHeader, 
  NLayoutContent, 
  NH2, 
  NButton,
  NModal, 
  NCode,
  NSpace,
  NDropdown,
  useMessage
} from 'naive-ui';
import { useDataManager } from '@/store/dataManager';
import { useFileSystem } from '@/composables/useFileSystem';
import { embedDataInPng } from '@/utils/pngProcessor';
import CharacterEditor from '../components/CharacterEditor.vue';
import { storeToRefs } from 'pinia';

const dataManager = useDataManager();
const message = useMessage();
const { editorCard } = storeToRefs(dataManager);
const { saveFileAs } = useFileSystem();
const jsonData = ref('');
const showJsonPreview = ref(false);

const exportOptions = [
  { label: '导出为 JSON', key: 'json' },
  { label: '导出为 PNG', key: 'png' }
];

const updateJsonDisplay = () => {
  try {
    jsonData.value = JSON.stringify(dataManager.getEditorCard(), null, 2);
  } catch (error) {
    jsonData.value = 'JSON数据加载失败';
    console.error('JSON数据加载失败:', error);
  }
};

const handleExportSelect = (key: 'json' | 'png') => {
  if (key === 'json') {
    exportAsJson();
  } else if (key === 'png') {
    exportAsPng();
  }
};

const exportAsJson = async () => {
  const cardData = dataManager.getEditorCard();
  await saveFileAs(cardData, {
    suggestedName: `${cardData.name || 'character'}.json`,
    types: [{
      description: 'Character Card',
      accept: { 'application/json': ['.json'] }
    }]
  });
};

const exportAsPng = async () => {
  const cardData = dataManager.getEditorCard();
  if (!cardData.avatar_data_url) {
    message.error('无法导出为PNG，因为缺少角色头像数据 (avatar_data_url)。请先上传头像。');
    return;
  }

  try {
    const blob = await embedDataInPng(cardData, cardData.avatar_data_url);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${cardData.name || 'character'}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    message.success('PNG 角色卡已开始下载。');
  } catch (error) {
    console.error('导出PNG失败:', error);
    message.error(`导出PNG失败: ${error instanceof Error ? error.message : '未知错误'}`);
  }
};

watch(editorCard, updateJsonDisplay, { deep: true });

onMounted(updateJsonDisplay);
</script>

<style scoped>
.editor-header {
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}
</style>
