<template>
  <n-layout style="height: 100%">
    <n-layout-header bordered class="editor-header">
      <n-h2 style="margin: 0;">角色卡编辑器</n-h2>
      <n-button @click="showJsonPreview = true">预览 JSON</n-button>
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
  NCode 
} from 'naive-ui';
import { useDataManager } from '@/store/dataManager';
import CharacterEditor from '../components/CharacterEditor.vue';
import { storeToRefs } from 'pinia';

const dataManager = useDataManager();
const { characterData } = storeToRefs(dataManager);
const jsonData = ref('');
const showJsonPreview = ref(false);

const updateJsonDisplay = () => {
  try {
    jsonData.value = JSON.stringify(dataManager.getFullData(), null, 2);
  } catch (error) {
    jsonData.value = 'JSON数据加载失败';
    console.error('JSON数据加载失败:', error);
  }
};

watch(characterData, updateJsonDisplay, { deep: true });

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
