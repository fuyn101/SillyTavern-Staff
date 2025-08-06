<template>
  <n-layout style="height: 100vh;">
    <n-layout-header bordered class="editor-header">
      <n-h1 style="margin: 0;">角色卡编辑器</n-h1>
      <CharacterPreview :jsonData="jsonData" />
    </n-layout-header>
    <n-layout-content>
      <character-editor />
    </n-layout-content>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { NLayout, NLayoutHeader, NLayoutContent, NH1 } from 'naive-ui';
import CharacterEditor from '@/features/character-editor/components/CharacterEditor.vue';
import CharacterPreview from '@/features/character-editor/components/CharacterPreview.vue';
import { useDataManager } from '@/store/dataManager';

const dataManager = useDataManager();
const jsonData = ref('');

const updateJsonDisplay = () => {
  try {
    jsonData.value = JSON.stringify(dataManager.getFullData(), null, 2);
  } catch (error) {
    jsonData.value = 'JSON数据加载失败';
    console.error('JSON数据加载失败:', error);
  }
};

watch(() => dataManager.characterData, updateJsonDisplay, { deep: true });

onMounted(updateJsonDisplay);
</script>

<style scoped>
.editor-header {
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  font-size: 18px;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}
</style>
