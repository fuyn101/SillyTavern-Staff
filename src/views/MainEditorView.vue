<template>
  <n-split direction="horizontal" style="height: 100vh">
    <template #1>
      <main-component ref="leftComponent" />
    </template>
    <template #2>
      <main-component ref="rightComponent" />
    </template>
  </n-split>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NSplit } from 'naive-ui';
import MainComponent from '@/components/common/MainComponent.vue';

const leftComponent = ref<InstanceType<typeof MainComponent> | null>(null);
const rightComponent = ref<InstanceType<typeof MainComponent> | null>(null);
</script>
