<template>
  <n-split v-if="presetsReady" direction="horizontal" style="height: 100vh">
    <template #1>
      <preset-editor side="left" />
    </template>
    <template #2>
      <preset-editor side="right" />
    </template>
  </n-split>
  <div v-else>
    Loading presets...
  </div>
</template>

<script setup lang="ts">
import { NSplit } from 'naive-ui';
import PresetEditor from '@/components/editor/PresetEditor.vue';
import { useDataManager } from '@/store/dataManager';
import { storeToRefs } from 'pinia';

const dataManager = useDataManager();
const { presetsReady } = storeToRefs(dataManager);
</script>
