<template>
  <n-split direction="horizontal" style="height: 100vh">
    <template #1>
      <preset-editor ref="leftComponent" type="preset" />
    </template>
    <template #2>
      <preset-editor ref="rightComponent" type="preset" />
    </template>
  </n-split>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NSplit } from 'naive-ui';
import PresetEditor from '@/components/editor/PresetEditor.vue';

const leftComponent = ref<InstanceType<typeof PresetEditor> | null>(null);
const rightComponent = ref<InstanceType<typeof PresetEditor> | null>(null);
</script>
