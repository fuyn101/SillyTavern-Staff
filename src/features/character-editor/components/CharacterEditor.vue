<template>
  <div class="editor-content">
    <n-tabs type="line" animated class="editor-tabs">
      <!-- 第一个标签页：编辑角色.json -->
      <n-tab-pane name="BasicContent" tab="编辑基础内容">
        <CharacterBasicEditor />
      </n-tab-pane>

      <!-- 第二个标签页：编辑data -->
      <n-tab-pane name="data" tab="编辑data">
        <CharacterDataEditor />
      </n-tab-pane>

      <!-- 第三个标签页：编辑提示词 -->
      <n-tab-pane name="prompts" tab="编辑提示词">
        <PromptsTab :prompts="prompts" @update:prompts="updatePrompts" />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { NTabs, NTabPane } from 'naive-ui';
import CharacterBasicEditor from './CharacterBasicEditor.vue';
import CharacterDataEditor from './CharacterDataEditor.vue';
import PromptsTab from './PromptsTab.vue';
import { useDataManager } from '@/store/dataManager';
import { storeToRefs } from 'pinia';

const dataManager = useDataManager();
const { prompts } = storeToRefs(dataManager);

const updatePrompts = (newPrompts: any[]) => {
  dataManager.updatePrompts(newPrompts);
};

</script>

<style scoped>
.editor-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: 24px;
  height: 100%;
  box-sizing: border-box;
}

.editor-tabs {
  height: 100%;
}
</style>
