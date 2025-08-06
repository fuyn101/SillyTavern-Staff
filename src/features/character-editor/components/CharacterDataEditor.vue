<template>
  <n-form
    ref="formRef"
    :model="formData"
    label-placement="top"
    class="data-editor-form"
  >
    <n-space vertical size="large">
      <!-- 基础数据 -->
      <n-card title="基础数据" :bordered="false" header-style="padding-bottom: 8px;">
        <CharacterBasicData :formData="formData" />
      </n-card>

      <n-divider />

      <!-- 拓展用字段 -->
      <n-card title="拓展用字段" :bordered="false" header-style="padding-bottom: 8px;">
        <CharacterExtensions :formData="formData" />
      </n-card>

      <n-divider />

      <!-- 角色书 / 世界观设定 -->
      <n-card title="角色书 / 世界观设定" :bordered="false" header-style="padding-bottom: 8px;">
        <CharacterBook :formData="formData" />
      </n-card>
    </n-space>
  </n-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { FormInst } from 'naive-ui';
import { useDataManager } from '@/store/dataManager';
import CharacterBasicData from './tabs/CharacterBasicData.vue';
import CharacterExtensions from './tabs/CharacterExtensions.vue';
import CharacterBook from './tabs/CharacterBook.vue';
import { NForm, NSpace, NCard, NDivider } from 'naive-ui';

const formRef = ref<FormInst | null>(null);
const dataManager = useDataManager();
const formData = computed(() => dataManager.characterData.data);

watch(formData, () => {
  // Logic for data change can be added here
}, { deep: true });
</script>

<style scoped>
.data-editor-form {
  padding: 8px;
}
</style>
