<template>
  <n-split direction="horizontal" style="height: 100vh">
    <template #1>
      <preset-editor :initial-data="leftInitialData" />
    </template>
    <template #2>
      <preset-editor :initial-data="rightInitialData" />
    </template>
  </n-split>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NSplit } from 'naive-ui';
import PresetEditor from '@/components/editor/PresetEditor.vue';
import { useRoute } from 'vue-router';

const leftInitialData = ref<object | undefined>(undefined);
const rightInitialData = ref<object | undefined>(undefined);
const route = useRoute();

onMounted(() => {
  // history.state is not always reliable, especially with HMR.
  // Vue router's state is the recommended way.
  const state = history.state || route.meta.state;
  if (state && state.presetData) {
    if (state.targetSide === 'left') {
      leftInitialData.value = state.presetData;
    } else if (state.targetSide === 'right') {
      rightInitialData.value = state.presetData;
    } else {
      // Fallback for old behavior or if targetSide is not specified
      leftInitialData.value = state.presetData;
    }
  }
});
</script>
