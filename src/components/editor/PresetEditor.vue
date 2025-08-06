<template>
  <n-card>
    <n-tabs type="line" animated>
      <n-tab-pane name="prompts" tab="提示词管理">
        <prompts-tab :prompts="jsonData.prompts" :order="jsonData.prompt_order" @update:prompts="updatePrompts" @update:order="updateOrder" />
      </n-tab-pane>
      <n-tab-pane name="settings" tab="设置">
        <merged-settings :settings="jsonData" @update:settings="updateSettings" />
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
import { reactive, onMounted, watch } from 'vue';
import { NCard, NTabs, NTabPane, NButton } from 'naive-ui';
import PromptsTab from '@/components/prompt/PromptsTab.vue';
import MergedSettings from '@/components/settings/MergedSettings.vue';
import { useFileSystem } from '@/composables/useFileSystem';
import defaultPreset from '@/assets/Default prompt.json';

const props = defineProps<{
  initialData?: object;
}>();

const { openFile, saveFile, saveFileAs } = useFileSystem();

const jsonData = reactive<any>({
  prompts: [],
  prompt_order: [],
});

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

function updateOrder(newOrder: any[]) {
  jsonData.prompt_order = newOrder;
}

function updateSettings(newSettings: any) {
  Object.assign(jsonData, newSettings);
}

async function handleOpenFile() {
  const data = await openFile(filePickerOptions);
  if (data) {
    Object.assign(jsonData, data);
  }
}

function handleSaveFile() {
  saveFile(jsonData);
}

function handleSaveFileAs() {
  saveFileAs(jsonData, filePickerOptions);
}

function loadDefaultPreset() {
  Object.assign(jsonData, defaultPreset);
}

watch(() => props.initialData, (newData) => {
  if (newData) {
    Object.assign(jsonData, newData);
  }
}, { immediate: true });

onMounted(() => {
  if (props.initialData) {
    Object.assign(jsonData, props.initialData);
  }
});
</script>
