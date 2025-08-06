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
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { NTabs, NTabPane } from 'naive-ui';
import CharacterBasicEditor from './CharacterBasicEditor.vue';
import CharacterDataEditor from './CharacterDataEditor.vue';
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
