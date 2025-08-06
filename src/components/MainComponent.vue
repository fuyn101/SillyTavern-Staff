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
      <n-button @click="openFile">打开</n-button>
      <n-button @click="saveFile">保存</n-button>
      <n-button @click="saveAsFile">另存为</n-button>
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import PromptsTab from '@/components/prompt/PromptsTab.vue';
import MergedSettings from '@/components/settings/MergedSettings.vue';

const jsonData = reactive<any>({
  prompts: [],
  prompt_order: [],
});

function updatePrompts(newPrompts: any[]) {
  jsonData.prompts = newPrompts;
}

function updateOrder(newOrder: any[]) {
  jsonData.prompt_order = newOrder;
}

function updateSettings(newSettings: any) {
  Object.assign(jsonData, newSettings);
}

let fileHandle: FileSystemFileHandle | null = null;

async function openFile() {
  try {
    [fileHandle] = await window.showOpenFilePicker({
      types: [
        {
          description: 'JSON Files',
          accept: {
            'application/json': ['.json'],
          },
        },
      ],
    });
    const file = await fileHandle.getFile();
    const contents = await file.text();
    const data = JSON.parse(contents);
    Object.assign(jsonData, data);
  } catch (err) {
    console.error('Error opening file:', err);
  }
}

async function saveFile() {
  if (!fileHandle) {
    saveAsFile();
    return;
  }
  try {
    const writable = await fileHandle.createWritable();
    await writable.write(JSON.stringify(jsonData, null, 2));
    await writable.close();
  } catch (err) {
    console.error('Error saving file:', err);
  }
}

async function saveAsFile() {
  try {
    const newFileHandle = await window.showSaveFilePicker({
      types: [
        {
          description: 'JSON Files',
          accept: {
            'application/json': ['.json'],
          },
        },
      ],
    });
    fileHandle = newFileHandle;
    const writable = await newFileHandle.createWritable();
    await writable.write(JSON.stringify(jsonData, null, 2));
    await writable.close();
  } catch (err) {
    console.error('Error saving file as:', err);
  }
}
</script>
