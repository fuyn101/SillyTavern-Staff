<template>
  <n-split direction="horizontal" style="height: 100vh">
    <template #1>
      <preset-editor ref="leftComponent" :initial-data="initialPreset" />
    </template>
    <template #2>
      <preset-editor ref="rightComponent" />
    </template>
  </n-split>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NSplit } from 'naive-ui';
import PresetEditor from '@/components/editor/PresetEditor.vue';

const leftComponent = ref<InstanceType<typeof PresetEditor> | null>(null);
const rightComponent = ref<InstanceType<typeof PresetEditor> | null>(null);
const initialPreset = ref<object | undefined>(undefined);

onMounted(() => {
  if (history.state && history.state.presetData) {
    initialPreset.value = history.state.presetData;
  }
});
</script>
