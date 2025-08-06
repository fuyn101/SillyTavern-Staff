<template>
  <n-space vertical size="large">
    <!-- 通用拓展 -->
    <n-h4 prefix="bar">通用拓展</n-h4>
    <n-grid :cols="12" :x-gap="24" :y-gap="8">
      <n-form-item-gi :span="3" label="健谈程度" path="extensions.talkativeness">
        <n-input-number
          :value="extensionsTalkativenessNumber"
          @update:value="updateExtensionsTalkativeness"
          :min="0" :max="1" :step="0.1"
        />
      </n-form-item-gi>
      <n-form-item-gi :span="3" label="世界" path="extensions.world">
        <n-input v-model:value="formData.extensions.world" placeholder="世界名称" />
      </n-form-item-gi>
      <n-form-item-gi :span="3" label="收藏" path="extensions.fav">
        <n-switch v-model:value="formData.extensions.fav" />
      </n-form-item-gi>
    </n-grid>

    <!-- 深度提示 -->
    <n-h4 prefix="bar">深度提示</n-h4>
    <n-grid :cols="12" :x-gap="24" :y-gap="8">
      <n-form-item-gi :span="3" label="深度" path="extensions.depth_prompt.depth">
        <n-input-number v-model:value="formData.extensions.depth_prompt.depth" :min="1" :max="10" />
      </n-form-item-gi>
      <n-form-item-gi :span="9" label="角色" path="extensions.depth_prompt.role">
        <n-input v-model:value="formData.extensions.depth_prompt.role" placeholder="角色" />
      </n-form-item-gi>
      <n-form-item-gi :span="12" label="提示内容" path="extensions.depth_prompt.prompt">
        <n-input v-model:value="formData.extensions.depth_prompt.prompt" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
    </n-grid>

    <!-- 正则脚本 -->
    <n-h4 prefix="bar">正则脚本</n-h4>
    <n-dynamic-input
      v-model:value="formData.extensions.regex_scripts"
      :on-create="handleCreateRegexScript"
      #="{ value: script, index }"
    >
      <n-card :title="script.scriptName || `脚本 ${index + 1}`" size="small" style="width: 100%">
        <n-space vertical>
          <n-grid :cols="12" :x-gap="12" :y-gap="8">
            <n-form-item-gi :span="4" label="脚本名称">
              <n-input v-model:value="script.scriptName" />
            </n-form-item-gi>
            <n-form-item-gi :span="4" label="查找正则">
              <n-input v-model:value="script.findRegex" />
            </n-form-item-gi>
            <n-form-item-gi :span="4" label="替换字符串">
              <n-input v-model:value="script.replaceString" />
            </n-form-item-gi>
            <n-form-item-gi :span="12" label="裁剪字符串">
              <n-dynamic-input v-model:value="script.trimStrings" :on-create="() => ''" />
            </n-form-item-gi>
            <n-form-item-gi :span="12" label="放置位置">
              <n-dynamic-tags v-model:value="script.placement" />
            </n-form-item-gi>
            <n-form-item-gi :span="2" label="禁用"><n-switch v-model:value="script.disabled" /></n-form-item-gi>
            <n-form-item-gi :span="2" label="仅MD"><n-switch v-model:value="script.markdownOnly" /></n-form-item-gi>
            <n-form-item-gi :span="2" label="仅提示"><n-switch v-model:value="script.promptOnly" /></n-form-item-gi>
            <n-form-item-gi :span="2" label="编辑时运行"><n-switch v-model:value="script.runOnEdit" /></n-form-item-gi>
            <n-form-item-gi :span="4" label="替换正则类型">
              <n-input-number v-model:value="script.substituteRegex" :min="0" />
            </n-form-item-gi>
            <n-form-item-gi :span="6" label="最小深度">
              <n-input-number v-model:value="script.minDepth" />
            </n-form-item-gi>
            <n-form-item-gi :span="6" label="最大深度">
              <n-input-number v-model:value="script.maxDepth" />
            </n-form-item-gi>
          </n-grid>
        </n-space>
      </n-card>
    </n-dynamic-input>
  </n-space>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NGrid, NFormItemGi, NInput, NInputNumber, NSwitch, NDynamicTags, NDynamicInput, NSpace, NH4, NCard } from 'naive-ui';

const props = defineProps<{
  formData: any
}>();

const extensionsTalkativenessNumber = computed(() => {
  const stringValue = props.formData.extensions?.talkativeness;
  return typeof stringValue === 'string' ? parseFloat(stringValue) || 0.5 : stringValue || 0.5;
});

const updateExtensionsTalkativeness = (value: number | null) => {
  props.formData.extensions.talkativeness = value === null ? '0.5' : value.toString();
};

const generateUUID = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
  const r = (Math.random() * 16) | 0;
  const v = c === 'x' ? r : (r & 0x3) | 0x8;
  return v.toString(16);
});

const handleCreateRegexScript = () => ({
  id: generateUUID(),
  scriptName: '',
  findRegex: '',
  replaceString: '',
  trimStrings: [],
  placement: [],
  disabled: false,
  markdownOnly: true,
  promptOnly: true,
  runOnEdit: false,
  substituteRegex: 0,
  minDepth: null,
  maxDepth: null,
});
</script>
