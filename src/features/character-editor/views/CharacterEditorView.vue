<template>
  <n-layout style="height: 100%">
    <n-layout-header bordered class="editor-header">
      <n-space align="center">
        <n-h2 style="margin: 0;">角色卡编辑器</n-h2>
        <n-button-group>
          <n-button 
            :type="activeTab === 'basic' ? 'primary' : 'default'" 
            @click="activeTab = 'basic'"
          >
            编辑基础内容
          </n-button>
          <n-button 
            :type="activeTab === 'data' ? 'primary' : 'default'" 
            @click="activeTab = 'data'"
          >
            编辑Data
          </n-button>
        </n-button-group>
      </n-space>
      <n-button @click="showJsonPreview = true">预览 JSON</n-button>
    </n-layout-header>
    <n-layout-content style="height: 90%;">
      <character-editor :active-tab="activeTab" />
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
  NButtonGroup,
  NSpace,
  NModal, 
  NCode 
} from 'naive-ui';
import CharacterEditor from '@/features/character-editor/components/CharacterEditor.vue';
import { useDataManager } from '@/store/dataManager';
import { storeToRefs } from 'pinia';

const dataManager = useDataManager();
const { characterData } = storeToRefs(dataManager);
const jsonData = ref('');
const showJsonPreview = ref(false);
const activeTab = ref('basic');

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
