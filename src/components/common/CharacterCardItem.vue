<template>
  <n-list-item>
    <div class="card-layout">
      <n-checkbox :value="card.name" :checked="isSelected" @update:checked="toggleSelection" style="margin-right: 16px;" />
      <img :src="card.avatar_data_url" v-if="card.avatar_data_url" class="side-avatar">
      <n-card :title="card.name" class="card-content">
        <p>{{ card.description }}</p>
        <template #action>
          <n-space>
            <n-button @click="emit('load', card.name)">加载</n-button>
            <n-popconfirm @positive-click="emit('delete', card.name)">
              <template #trigger>
                <n-button type="error">删除</n-button>
              </template>
              确定要删除角色卡 "{{ card.name }}" 吗？
            </n-popconfirm>
          </n-space>
        </template>
      </n-card>
    </div>
  </n-list-item>
</template>

<script setup lang="ts">
import { NListItem, NCheckbox, NCard, NSpace, NButton, NPopconfirm } from 'naive-ui';
import type { CharacterData } from '@/store/dataManager';

const props = defineProps<{
  card: CharacterData;
  isSelected: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:selected', name: string, checked: boolean): void;
  (e: 'load', name: string): void;
  (e: 'delete', name: string): void;
}>();

const toggleSelection = (checked: boolean) => {
  emit('update:selected', props.card.name, checked);
};
</script>

<style scoped>
.card-layout {
  display: flex;
  align-items: flex-start;
}
.side-avatar {
  width: 128px;
  height: 192px;
  object-fit: cover;
  margin-right: 24px;
  border-radius: 4px;
}
.card-content {
  flex: 1;
}
</style>
