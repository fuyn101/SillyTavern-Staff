<template>
  <n-space v-if="formData.character_book" vertical size="large">
    <n-form-item label="世界书名称" path="character_book.name">
      <n-input v-model:value="formData.character_book.name" placeholder="请输入世界书名称" />
    </n-form-item>

    <n-h4 prefix="bar">条目</n-h4>
    <n-dynamic-input
      v-model:value="formData.character_book.entries"
      :on-create="handleCharacterBookAdd"
      #="{ value: entry, index }"
    >
      <n-collapse>
        <n-collapse-item :title="entry.comment || `条目 ${index + 1}`" :name="entry.id" style="width: 100%">
          <n-space vertical>
            <!-- 核心内容 -->
            <n-grid :cols="12" :x-gap="12" :y-gap="8">
            <n-form-item-gi :span="12" label="条目名称 (注释)">
              <n-input v-model:value="entry.comment" />
            </n-form-item-gi>
            <n-form-item-gi :span="12" label="内容">
              <n-input v-model:value="entry.content" type="textarea" :autosize="{ minRows: 3 }" />
            </n-form-item-gi>
          </n-grid>

          <!-- 关键词 -->
          <n-grid :cols="12" :x-gap="12" :y-gap="8">
            <n-form-item-gi :span="6" label="主要关键词">
              <n-dynamic-tags v-model:value="entry.keys" />
            </n-form-item-gi>
            <n-form-item-gi :span="6" label="次要关键词">
              <n-dynamic-tags v-model:value="entry.secondary_keys" />
            </n-form-item-gi>
          </n-grid>

          <!-- 高级设置 -->
          <n-grid :cols="12" :x-gap="12" :y-gap="8">
            <n-form-item-gi :span="2" label="启用"><n-switch v-model:value="entry.enabled" /></n-form-item-gi>
            <n-form-item-gi :span="2" label="常量"><n-switch v-model:value="entry.constant" /></n-form-item-gi>
            <n-form-item-gi :span="2" label="选择性"><n-switch v-model:value="entry.selective" /></n-form-item-gi>
            <n-form-item-gi :span="2" label="正则"><n-switch v-model:value="entry.use_regex" /></n-form-item-gi>
            <n-form-item-gi :span="4" label="位置">
              <n-select v-model:value="entry.position" :options="positionOptions" />
            </n-form-item-gi>
            <n-form-item-gi :span="4" label="插入顺序">
              <n-input-number v-model:value="entry.insertion_order" />
            </n-form-item-gi>
            <n-form-item-gi :span="4" label="扫描深度">
              <n-input-number v-model:value="entry.extensions.depth" />
            </n-form-item-gi>
            <n-form-item-gi :span="4" label="触发概率">
              <n-input-number v-model:value="entry.extensions.probability" :min="0" :max="100" />
            </n-form-item-gi>
          </n-grid>
        </n-space>
      </n-collapse-item>
    </n-collapse>
    </n-dynamic-input>
  </n-space>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { NGrid, NFormItemGi, NInput, NInputNumber, NSwitch, NDynamicTags, NDynamicInput, NSpace, NH4, NCollapse, NCollapseItem, NSelect, NFormItem } from 'naive-ui';

const props = defineProps<{
  formData: any
}>();

onMounted(() => {
  if (!props.formData.character_book) {
    props.formData.character_book = {
      name: '',
      entries: []
    };
  }
});

const positionOptions = [
  { label: '角色前', value: 'before_char' },
  { label: '角色后', value: 'after_char' },
  { label: '对话示例前', value: 'before_example' },
  { label: '对话示例后', value: 'after_example' },
];

const handleCharacterBookAdd = () => ({
  id: Date.now(),
  keys: [],
  secondary_keys: [],
  comment: '',
  content: '',
  constant: false,
  selective: false,
  insertion_order: 100,
  enabled: true,
  position: 'after_char',
  use_regex: false,
  extensions: {
    display_index: 0,
    probability: 100,
    depth: 4,
    role: 0,
  },
});
</script>
