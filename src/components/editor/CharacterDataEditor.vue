<template>
  <n-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    label-placement="top"
    label-width="80"
    require-mark-placement="right-hanging"
    size="small"
  >
    <n-tabs type="line" animated>
      <!-- 基础数据标签页 -->
      <n-tab-pane name="basic" tab="基础数据">
        <CharacterBasicData :formData="formData" />
      </n-tab-pane>

      <!-- 第二个标签页：Extensions 表单 -->
      <n-tab-pane name="extensions" tab="拓展用字段">
        <CharacterExtensions :formData="formData" />
      </n-tab-pane>

      <!-- 第三个标签页：世界书 -->
      <n-tab-pane name="character_book" tab="角色书 / 世界观设定">
        <CharacterBook :formData="formData" />
      </n-tab-pane>
    </n-tabs>
  </n-form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { FormInst, FormRules } from 'naive-ui'
import { useDataManager } from '@/store/dataManager'
import CharacterBasicData from '@/components/editor/tabs/CharacterBasicData.vue'
import CharacterExtensions from '@/components/editor/tabs/CharacterExtensions.vue'
import CharacterBook from '@/components/editor/tabs/CharacterBook.vue'

const formRef = ref<FormInst | null>(null)

// 使用数据管理器
const dataManager = useDataManager()

// 表单数据 - data字段内容
const formData = computed(() => dataManager.getDataField())

// 表单验证规则
const formRules: FormRules = {
  name: {
    required: true,
    message: '请输入数据名称',
    trigger: 'blur',
  },
  description: {
    required: true,
    message: '请输入数据描述',
    trigger: 'blur',
  },
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
    dataManager.saveDataFieldToLocalStorage()
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

    // 初始化当前选中的可选问候语标签页
    if (formData.value.alternate_greetings && formData.value.alternate_greetings.length > 0) {
      // 这个逻辑现在在 CharacterBasicData 组件内部处理
      // currentAlternateGreetingsTab.value = '0'
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
})

// 加载数据（供父组件调用）
const loadData = (data: any) => {
  if (data.data) {
    // 如果是完整数据，设置data字段
    dataManager.setDataField(data.data)
  } else {
    // 如果只是data字段数据
    dataManager.setDataField(data)
  }
  // 触发数据变化事件
  triggerDataChange()
}

// 获取数据（供父组件调用）
const getData = () => {
  return dataManager.getDataField()
}

// 暴露方法给父组件
defineExpose({
  loadData,
  getData,
})
</script>

<style scoped>
.n-form {
  background-color: transparent;
}

:deep(.n-form-item) {
  margin-bottom: 4px;
}

:deep(.n-input) {
  --n-height: 28px;
}

:deep(.n-input-number) {
  --n-height: 28px;
}

:deep(.n-dynamic-tags) {
  --n-height: 28px;
}

:deep(.n-tabs-nav) {
  padding: 4px 0;
}

:deep(.n-tab-pane) {
  padding: 8px 0;
}

:deep(.n-space) {
  --n-gap: 8px;
}
</style>
