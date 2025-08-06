<template>
  <n-grid :cols="24" :x-gap="12" :y-gap="8">
    <!-- 第一行：数据名称、创建者、角色版本、数据标签 -->
    <n-form-item-gi :span="6" label="数据名称" path="name">
      <n-input
        v-model:value="formData.name"
        placeholder="请输入数据名称"
        type="textarea"
        :rows="1"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="6" label="创作者" path="creator">
      <n-input
        v-model:value="formData.creator"
        placeholder="请输入创建者"
        type="textarea"
        :rows="1"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="6" label="角色卡版本号" path="character_version">
      <n-input
        v-model:value="formData.character_version"
        placeholder="请输入角色版本"
        type="textarea"
        :rows="1"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="6" label="标签" path="tags">
      <n-dynamic-tags v-model:value="formData.tags" size="small" />
    </n-form-item-gi>

    <!-- 第二行：数据描述、数据开场白 -->
    <n-form-item-gi :span="12" label="数据描述" path="description">
      <n-input
        v-model:value="formData.description"
        placeholder="请输入数据描述"
        type="textarea"
        :rows="3"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="12" label="数据开场白" path="first_mes">
      <n-input
        v-model:value="formData.first_mes"
        placeholder="请输入数据开场白"
        type="textarea"
        :rows="3"
        size="small"
      />
    </n-form-item-gi>

    <!-- 第三行：数据对话示例、创建者笔记、系统提示、历史后指令 -->
    <n-form-item-gi :span="6" label="数据对话示例" path="mes_example">
      <n-input
        v-model:value="formData.mes_example"
        placeholder="请输入数据对话示例"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="6" label="创作者备注" path="creator_notes">
      <n-input
        v-model:value="formData.creator_notes"
        placeholder="请输入创建者笔记"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="6" label="系统提示词" path="system_prompt">
      <n-input
        v-model:value="formData.system_prompt"
        placeholder="请输入系统提示"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="6" label="聊天后指令（又称后置指令）" path="post_history_instructions">
      <n-input
        v-model:value="formData.post_history_instructions"
        placeholder="请输入历史后指令"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <!-- 第四行：数据性格、数据场景、数据对话示例 -->
    <n-form-item-gi :span="8" label="数据性格" path="personality">
      <n-input
        v-model:value="formData.personality"
        placeholder="请输入数据性格"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="8" label="数据场景" path="scenario">
      <n-input
        v-model:value="formData.scenario"
        placeholder="请输入数据场景"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="8" label="数据对话示例" path="mes_example">
      <n-input
        v-model:value="formData.mes_example"
        placeholder="请输入数据对话示例"
        type="textarea"
        :rows="2"
        size="small"
      />
    </n-form-item-gi>

    <!-- 可选问候语 -->
    <n-form-item-gi :span="24" label="备用开场白" path="alternate_greetings">
      <n-tabs
        type="card"
        v-model:value="currentAlternateGreetingsTab"
        :addable="alternateGreetingsAddable"
        :closable="alternateGreetingsClosable"
        tab-style="min-width: 80px;"
        @close="handleAlternateGreetingsClose"
        @add="handleAlternateGreetingsAdd"
      >
        <n-tab-pane
          v-for="(greeting, index) in formData.alternate_greetings"
          :key="index"
          :name="index.toString()"
          :tab="`开局 ${index + 1}`"
        >
          <n-form-item :label="`开局 ${index + 1}`" :path="`alternate_greetings[${index}]`">
            <n-input
              v-model:value="formData.alternate_greetings[index]"
              type="textarea"
              :rows="3"
              placeholder="请输入开局剧情"
            />
          </n-form-item>
        </n-tab-pane>
      </n-tabs>
    </n-form-item-gi>

    <!-- 群组专用问候语 -->
    <n-form-item-gi :span="24" label="群组专用问候语" path="group_only_greetings">
      <n-dynamic-input
        v-model:value="formData.group_only_greetings"
        placeholder="请输入群组专用问候语"
        :on-create="() => ''"
      />
    </n-form-item-gi>
  </n-grid>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 定义 props
const props = defineProps<{
  formData: any
}>()

// 当前选中的可选问候语标签页
const currentAlternateGreetingsTab = ref<string>('')

// 计算属性：控制可选问候语添加按钮状态
const alternateGreetingsAddable = computed(() => {
  return {
    disabled: props.formData.alternate_greetings?.length >= 20,
  }
})

// 计算属性：控制可选问候语关闭按钮状态
const alternateGreetingsClosable = computed(() => {
  return props.formData.alternate_greetings?.length > 1
})

// 处理可选问候语添加标签页事件
const handleAlternateGreetingsAdd = () => {
  const greetings = props.formData.alternate_greetings
  if (!greetings) {
    props.formData.alternate_greetings = []
    return
  }

  // 添加新的空问候语
  greetings.push('')
  // 切换到新添加的问候语标签页
  currentAlternateGreetingsTab.value = (greetings.length - 1).toString()
}

// 处理可选问候语关闭标签页事件
const handleAlternateGreetingsClose = (tabName: string) => {
  const greetings = props.formData.alternate_greetings
  const index = parseInt(tabName)
  if (isNaN(index) || index < 0 || index >= greetings.length) return

  greetings.splice(index, 1)

  // 如果关闭的是当前选中的标签页，切换到相邻的标签页
  if (currentAlternateGreetingsTab.value === tabName) {
    const nextIndex = Math.min(index, greetings.length - 1)
    currentAlternateGreetingsTab.value = nextIndex >= 0 ? nextIndex.toString() : ''
  }
}
</script>

<style scoped>
/* 可以添加一些特定于此组件的样式 */
</style>
