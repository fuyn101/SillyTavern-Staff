<template>
  <n-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    label-placement="top"
    label-width="80"
    require-mark-placement="right-hanging"
    size="small"
    class="unified-editor"
  >
    <n-grid :cols="24" :x-gap="12" :y-gap="8">
      <!-- 第一行：四个字段 -->
      <n-form-item-gi :span="6" label="名称" path="name">
        <n-input v-model:value="formData.name" placeholder="角色名称" type="textarea" :rows="1" />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="头像" path="avatar">
        <n-input
          v-model:value="formData.avatar"
          placeholder="头像文件名"
          type="textarea"
          :rows="1"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="聊天记录" path="chat">
        <n-input
          v-model:value="formData.chat"
          placeholder="聊天记录标识"
          type="textarea"
          :rows="1"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="健谈程度" path="talkativeness">
        <n-input-number
          :value="talkativenessNumber"
          @update:value="updateTalkativeness"
          :min="0"
          :max="1"
          :step="0.1"
          placeholder="0-1"
          size="small"
        />
      </n-form-item-gi>

      <!-- 第二行：四个字段 -->
      <n-form-item-gi :span="6" label="收藏" path="fav">
        <n-switch v-model:value="formData.fav" size="small" />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="标签" path="tags">
        <n-dynamic-tags v-model:value="formData.tags" size="small" />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="规格" path="spec">
        <n-input
          v-model:value="formData.spec"
          placeholder="规格"
          type="textarea"
          :rows="1"
          readonly
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="规格版本" path="spec_version">
        <n-input
          v-model:value="formData.spec_version"
          placeholder="规格版本"
          type="textarea"
          :rows="1"
          readonly
        />
      </n-form-item-gi>

      <!-- 第三行：四个字段 -->
      <n-form-item-gi :span="6" label="创建日期" path="create_date">
        <n-input
          v-model:value="formData.create_date"
          placeholder="创建日期"
          type="textarea"
          :rows="1"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="个性" path="personality">
        <n-input
          v-model:value="formData.personality"
          type="textarea"
          :rows="2"
          placeholder="角色性格描述"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="场景" path="scenario">
        <n-input
          v-model:value="formData.scenario"
          type="textarea"
          :rows="2"
          placeholder="角色场景描述"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="对话示例" path="mes_example">
        <n-input
          v-model:value="formData.mes_example"
          type="textarea"
          :rows="2"
          placeholder="对话示例"
        />
      </n-form-item-gi>

      <!-- 第四行：创建者备注 -->
      <n-form-item-gi :span="6" label="创建者备注" path="creatorcomment">
        <n-input
          v-model:value="formData.creatorcomment"
          type="textarea"
          :rows="2"
          placeholder="创建者备注"
        />
      </n-form-item-gi>

      <!-- 第五行：描述占满一行 -->
      <n-form-item-gi :span="24" label="(角色)描述" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          :rows="3"
          placeholder="角色描述"
        />
      </n-form-item-gi>

      <!-- 第六行：开场白占满一行 -->
      <n-form-item-gi :span="24" label="开场白" path="first_mes">
        <n-input
          v-model:value="formData.first_mes"
          type="textarea"
          :rows="3"
          placeholder="角色开场白"
        />
      </n-form-item-gi>
    </n-grid>
  </n-form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { FormInst, FormRules } from 'naive-ui'
import { useDataManager } from '@/store/dataManager'

const formRef = ref<FormInst | null>(null)

// 使用数据管理器
const dataManager = useDataManager()

// 表单数据 - 基础数据部分
const formData = computed(() => dataManager.getBasicData())

// 表单验证规则
const formRules: FormRules = {
  name: {
    required: true,
    message: '请输入角色名称',
    trigger: 'blur',
  },
  description: {
    required: true,
    message: '请输入角色描述',
    trigger: 'blur',
  },
}

// 将字符串类型的talkativeness转换为数字类型供InputNumber使用
const talkativenessNumber = computed(() => {
  const stringValue = formData.value.talkativeness
  if (typeof stringValue === 'string') {
    return parseFloat(stringValue) || 0.5
  }
  return stringValue || 0.5
})

// 将数字类型的talkativeness转换回字符串类型保存到formData
const updateTalkativeness = (value: number | null) => {
  if (value === null) {
    formData.value.talkativeness = '0.5'
  } else {
    formData.value.talkativeness = value.toString()
  }
}

// 触发自定义事件通知数据变化
const triggerDataChange = () => {
  window.dispatchEvent(new CustomEvent('char-data-changed'))
}

// 监听表单数据变化
watch(
  formData,
  () => {
    // 自动保存到本地存储
    dataManager.saveBasicDataToLocalStorage()
    // 触发数据变化事件
    triggerDataChange()
  },
  { deep: true },
)

// 初始化数据
onMounted(async () => {
  try {
    // 尝试从本地存储加载数据
    const savedData = localStorage.getItem('character_full_data')
    if (savedData) {
      dataManager.loadFromJson(savedData)
    } else {
      // 重置为默认数据
      dataManager.resetToDefault()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
})

// 加载数据（供父组件调用）
const loadData = (data: any) => {
  if (data.data) {
    // 如果是完整数据
    dataManager.setFullData(data)
  } else {
    // 如果只是基础数据
    dataManager.setBasicData(data)
  }
  // 触发数据变化事件
  triggerDataChange()
}

// 获取数据（供父组件调用）
const getData = () => {
  return dataManager.getBasicData()
}

// 暴露方法给父组件
defineExpose({
  loadData,
  getData,
})
</script>

<style scoped>
.unified-editor {
  background-color: transparent;
}

.unified-editor :deep(.n-form-item) {
  margin-bottom: 4px;
}

.unified-editor :deep(.n-input) {
  --n-height: 28px;
}

.unified-editor :deep(.n-input-number) {
  --n-height: 28px;
}

.unified-editor :deep(.n-dynamic-tags) {
  --n-height: 28px;
}
</style>
