<template>
  <n-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    label-placement="top"
    class="basic-editor-form"
  >
    <n-space vertical size="large">
      <!-- 核心信息 -->
      <n-card title="核心信息" :bordered="false" header-style="padding-bottom: 8px;">
        <n-grid :cols="12" :x-gap="24">
          <n-form-item-gi :span="4" label="名称" path="name">
            <n-input v-model:value="formData.name" placeholder="角色名称" />
          </n-form-item-gi>
          <n-form-item-gi :span="8" label="标签" path="tags">
            <n-dynamic-tags v-model:value="formData.tags" />
          </n-form-item-gi>
          <n-form-item-gi :span="12" label="(角色)描述" path="description">
            <n-input
              v-model:value="formData.description"
              type="textarea"
              :autosize="{ minRows: 3 }"
              placeholder="角色的核心描述，会极大地影响其行为。"
            />
          </n-form-item-gi>
          <n-form-item-gi :span="12" label="开场白" path="first_mes">
            <n-input
              v-model:value="formData.first_mes"
              type="textarea"
              :autosize="{ minRows: 3 }"
              placeholder="角色的第一句话，用于开始对话。"
            />
          </n-form-item-gi>
        </n-grid>
      </n-card>

      <n-divider />

      <!-- 角色扮演 -->
      <n-card title="角色扮演" :bordered="false" header-style="padding-bottom: 8px;">
        <n-grid :cols="12" :x-gap="24">
          <n-form-item-gi :span="6" label="个性" path="personality">
            <n-input
              v-model:value="formData.personality"
              type="textarea"
              :autosize="{ minRows: 2 }"
              placeholder="角色的性格特点。"
            />
          </n-form-item-gi>
          <n-form-item-gi :span="6" label="场景" path="scenario">
            <n-input
              v-model:value="formData.scenario"
              type="textarea"
              :autosize="{ minRows: 2 }"
              placeholder="故事发生的背景或环境。"
            />
          </n-form-item-gi>
          <n-form-item-gi :span="12" label="对话示例" path="mes_example">
            <n-input
              v-model:value="formData.mes_example"
              type="textarea"
              :autosize="{ minRows: 4 }"
              placeholder="提供一些对话示例，帮助AI学习角色的语言风格。"
            />
          </n-form-item-gi>
        </n-grid>
      </n-card>

      <n-divider />

      <!-- 元数据 -->
      <n-card title="元数据" :bordered="false" header-style="padding-bottom: 8px;">
        <n-grid :cols="12" :x-gap="24" :y-gap="8">
          <n-form-item-gi :span="4" label="头像" path="avatar">
            <n-input v-model:value="formData.avatar" placeholder="avatar.png" />
          </n-form-item-gi>
          <n-form-item-gi :span="4" label="聊天记录" path="chat">
            <n-input v-model:value="formData.chat" placeholder="char_chat.jsonl" />
          </n-form-item-gi>
          <n-form-item-gi :span="4" label="健谈程度" path="talkativeness">
            <n-input-number
              :value="talkativenessNumber"
              @update:value="updateTalkativeness"
              :min="0"
              :max="1"
              :step="0.1"
            />
          </n-form-item-gi>
          <n-form-item-gi :span="4" label="创建日期" path="create_date">
            <n-input v-model:value="formData.create_date" />
          </n-form-item-gi>
          <n-form-item-gi :span="4" label="规格" path="spec">
            <n-input v-model:value="formData.spec" readonly />
          </n-form-item-gi>
          <n-form-item-gi :span="4" label="规格版本" path="spec_version">
            <n-input v-model:value="formData.spec_version" readonly />
          </n-form-item-gi>
          <n-form-item-gi :span="4" label="收藏" path="fav">
            <n-switch v-model:value="formData.fav" />
          </n-form-item-gi>
          <n-form-item-gi :span="8" label="创建者备注" path="creatorcomment">
            <n-input
              v-model:value="formData.creatorcomment"
              type="textarea"
              :autosize="{ minRows: 1 }"
            />
          </n-form-item-gi>
        </n-grid>
      </n-card>
    </n-space>
    <n-button @click="saveData" type="primary" style="margin-top: 24px;">保存更改</n-button>
  </n-form>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import type { FormInst, FormRules } from 'naive-ui'
import { useDataManager, type CharacterData } from '@/store/dataManager'
import { NForm, NSpace, NCard, NGrid, NFormItemGi, NInput, NDynamicTags, NDivider, NInputNumber, NSwitch } from 'naive-ui'

const formRef = ref<FormInst | null>(null)
const dataManager = useDataManager()
const formData = reactive<CharacterData>({} as CharacterData);

onMounted(() => {
  Object.assign(formData, JSON.parse(JSON.stringify(dataManager.characterData)));
});

watch(() => dataManager.characterData, (newData) => {
  Object.assign(formData, JSON.parse(JSON.stringify(newData)));
}, { deep: true });


const formRules: FormRules = {
  name: { required: true, message: '请输入角色名称', trigger: 'blur' },
  description: { required: true, message: '请输入角色描述', trigger: 'blur' },
}

const talkativenessNumber = computed(() => {
  const stringValue = formData.talkativeness
  return typeof stringValue === 'string' ? parseFloat(stringValue) || 0.5 : stringValue || 0.5
})

const updateTalkativeness = (value: number | null) => {
  formData.talkativeness = value === null ? '0.5' : value.toString()
}

const saveData = () => {
  dataManager.setFullData(JSON.parse(JSON.stringify(formData)));
};

</script>

<style scoped>
.basic-editor-form {
  padding: 8px;
}
</style>
