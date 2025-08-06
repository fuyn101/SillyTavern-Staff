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
    <n-button @click="saveData" type="primary" style="margin-top: 24px;">保存更改</n-button>
  </n-form>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import type { FormInst } from 'naive-ui';
import { useDataManager, type CharacterData } from '@/store/dataManager';
import CharacterBasicData from './tabs/CharacterBasicData.vue';
import CharacterExtensions from './tabs/CharacterExtensions.vue';
import CharacterBook from './tabs/CharacterBook.vue';
import { NForm, NSpace, NCard, NDivider } from 'naive-ui';

const formRef = ref<FormInst | null>(null);
const dataManager = useDataManager();
const formData = reactive<CharacterData['data']>({} as CharacterData['data']);

onMounted(() => {
  Object.assign(formData, JSON.parse(JSON.stringify(dataManager.characterData.data)));
});

watch(() => dataManager.characterData.data, (newData) => {
  Object.assign(formData, JSON.parse(JSON.stringify(newData)));
}, { deep: true });

const saveData = () => {
  dataManager.characterData.data = JSON.parse(JSON.stringify(formData));
};
</script>

<style scoped>
.data-editor-form {
  padding: 8px;
}
</style>
