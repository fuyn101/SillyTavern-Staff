<template>
  <n-card>
    <n-tabs type="line" animated>
      <n-tab-pane name="prompts" tab="提示词管理">
        <prompts-tab :prompts="jsonData.prompts" @update:prompts="updatePrompts" />
      </n-tab-pane>
      <n-tab-pane name="settings" tab="设置">
        <prompt-settings :settings="jsonData" @update:settings="updateSettings" />
      </n-tab-pane>
    </n-tabs>
    <template #action>
      <n-button @click="handleOpenFile">打开</n-button>
      <n-button @click="handleSaveFile">保存</n-button>
      <n-button @click="handleSaveFileAs">另存为</n-button>
      <n-button @click="loadDefaultPreset">加载默认预设</n-button>
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { reactive, watch, toRefs } from 'vue';
import { NCard, NTabs, NTabPane, NButton } from 'naive-ui';
import PromptsTab from '@/features/character-editor/components/PromptsTab.vue';
import PromptSettings from '@/components/prompt/PromptSettings.vue';
import { useFileSystem } from '@/composables/useFileSystem';
import defaultPreset from '@/assets/Default prompt.json';
import { useDataManager } from '@/store/dataManager';

const props = defineProps<{
  side: 'left' | 'right';
}>();

const { openFile, saveFile, saveFileAs } = useFileSystem();
const dataManager = useDataManager();

// jsonData is now a direct reference to the reactive state in the store
const jsonData = props.side === 'left' ? dataManager.presetEditorLeft : dataManager.presetEditorRight;

const filePickerOptions: FilePickerOptions = {
  types: [
    {
      description: 'JSON Files',
      accept: { 'application/json': ['.json'] },
    },
  ],
};

function updatePrompts(newPrompts: any[]) {
  jsonData.prompts = newPrompts;
}


function updateSettings(newSettings: any) {
  // No need to Object.assign, direct mutation is fine for reactive objects
  for (const key in newSettings) {
    jsonData[key] = newSettings[key];
  }
}

async function handleOpenFile() {
  const data = await openFile(filePickerOptions);
  if (data) {
    dataManager.updatePresetEditorData(props.side, data);
  }
}

function handleSaveFile() {
  saveFile(jsonData);
}

function handleSaveFileAs() {
  saveFileAs(jsonData, filePickerOptions);
}

function loadDefaultPreset() {
  dataManager.updatePresetEditorData(props.side, defaultPreset);
}

// Watch for changes in jsonData and persist them to IndexedDB
watch(jsonData, (newData) => {
  // The data is already reactive. We just need to trigger the save.
  dataManager.updatePresetEditorData(props.side, newData);
}, { deep: true });
</script>
