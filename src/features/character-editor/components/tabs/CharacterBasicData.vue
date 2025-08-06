<template>
  <n-space vertical size="large">
    <!-- 元数据 -->
    <n-h4 prefix="bar">元数据</n-h4>
    <n-grid :cols="12" :x-gap="24" :y-gap="8">
      <n-form-item-gi :span="4" label="数据名称" path="name">
        <n-input v-model:value="formData.name" placeholder="请输入数据名称" />
      </n-form-item-gi>
      <n-form-item-gi :span="4" label="创作者" path="creator">
        <n-input v-model:value="formData.creator" placeholder="请输入创建者" />
      </n-form-item-gi>
      <n-form-item-gi :span="4" label="角色卡版本号" path="character_version">
        <n-input v-model:value="formData.character_version" placeholder="请输入角色版本" />
      </n-form-item-gi>
      <n-form-item-gi :span="12" label="标签" path="tags">
        <n-dynamic-tags v-model:value="formData.tags">
          <template #trigger="{ activate, disabled }">
            <n-button size="small" type="primary" dashed :disabled="disabled" @click="activate">
              <template #icon>
                <n-icon><add-icon /></n-icon>
              </template>
              添加
            </n-button>
          </template>
        </n-dynamic-tags>
      </n-form-item-gi>
    </n-grid>

    <!-- 核心定义 -->
    <n-h4 prefix="bar">核心定义</n-h4>
    <n-grid :cols="12" :x-gap="24" :y-gap="8">
      <n-form-item-gi :span="12" label="数据描述" path="description">
        <n-input v-model:value="formData.description" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
      <n-form-item-gi :span="6" label="数据性格" path="personality">
        <n-input v-model:value="formData.personality" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
      <n-form-item-gi :span="6" label="数据场景" path="scenario">
        <n-input v-model:value="formData.scenario" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
      <n-form-item-gi :span="12" label="数据对话示例" path="mes_example">
        <n-input v-model:value="formData.mes_example" type="textarea" :autosize="{ minRows: 3 }" />
      </n-form-item-gi>
    </n-grid>
    
    <!-- 问候语 -->
    <n-h4 prefix="bar">问候语</n-h4>
    <n-grid :cols="12" :x-gap="24" :y-gap="8">
      <n-form-item-gi :span="12" label="数据开场白" path="first_mes">
        <n-input v-model:value="formData.first_mes" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
      <n-form-item-gi :span="12" label="备用开场白" path="alternate_greetings">
        <n-dynamic-input
          v-model:value="formData.alternate_greetings"
          placeholder="请输入备用开场白"
          :on-create="() => ''"
        />
      </n-form-item-gi>
    </n-grid>

    <!-- 高级设定 -->
    <n-h4 prefix="bar">高级设定</n-h4>
    <n-grid :cols="12" :x-gap="24" :y-gap="8">
      <n-form-item-gi :span="12" label="创作者备注" path="creator_notes">
        <n-input v-model:value="formData.creator_notes" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
      <n-form-item-gi :span="12" label="系统提示词" path="system_prompt">
        <n-input v-model:value="formData.system_prompt" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
      <n-form-item-gi :span="12" label="聊天后指令（又称后置指令）" path="post_history_instructions">
        <n-input v-model:value="formData.post_history_instructions" type="textarea" :autosize="{ minRows: 2 }" />
      </n-form-item-gi>
    </n-grid>
  </n-space>
</template>

<script setup lang="ts">
import { Add as AddIcon } from '@vicons/ionicons5';
defineProps<{
  formData: any
}>();
</script>
