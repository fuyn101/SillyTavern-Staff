<template>
  <n-grid :cols="24" :x-gap="12" :y-gap="8">
    <n-form-item-gi :span="8" label="健谈程度" path="extensions.talkativeness">
      <n-input-number
        :value="extensionsTalkativenessNumber"
        @update:value="updateExtensionsTalkativeness"
        :min="0"
        :max="1"
        :step="0.1"
        placeholder="请输入健谈程度 (0-1)"
      />
    </n-form-item-gi>

    <n-form-item-gi :span="8" label="收藏" path="extensions.fav">
      <n-switch v-model:value="formData.extensions.fav" />
    </n-form-item-gi>

    <n-form-item-gi :span="8" label="世界" path="extensions.world">
      <n-input
        v-model:value="formData.extensions.world"
        placeholder="请输入世界名称"
        type="textarea"
        :rows="1"
      />
    </n-form-item-gi>
  </n-grid>

  <n-form-item label="深度提示" path="extensions.depth_prompt">
    <n-grid :cols="24" :x-gap="12" :y-gap="8">
      <n-form-item-gi :span="12" label="提示内容" path="extensions.depth_prompt.prompt">
        <n-input
          v-model:value="formData.extensions.depth_prompt.prompt"
          type="textarea"
          :rows="2"
          placeholder="请输入提示内容"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="深度" path="extensions.depth_prompt.depth">
        <n-input-number
          v-model:value="formData.extensions.depth_prompt.depth"
          :min="1"
          :max="10"
          placeholder="请输入深度"
        />
      </n-form-item-gi>

      <n-form-item-gi :span="6" label="角色" path="extensions.depth_prompt.role">
        <n-input
          v-model:value="formData.extensions.depth_prompt.role"
          placeholder="请输入角色"
          type="textarea"
          :rows="2"
        />
      </n-form-item-gi>
    </n-grid>
  </n-form-item>

  <!-- Regex Scripts Tabs -->
  <n-form-item label="正则脚本">
    <n-tabs
      type="card"
      v-model:value="currentRegexScriptTab"
      :addable="addable"
      :closable="closable"
      tab-style="min-width: 80px;"
      @close="handleClose"
      @add="handleAdd"
    >
      <n-tab-pane
        v-for="(script, index) in formData.extensions.regex_scripts"
        :key="script.id"
        :name="script.id"
        :tab="script.scriptName || `脚本 ${index + 1}`"
      >
        <n-space vertical>
          <!-- 脚本名称、查找正则、替换字符串：8*3 2row -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="8"
              :label="`脚本名称 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].scriptName`"
            >
              <n-input
                v-model:value="formData.extensions.regex_scripts[index].scriptName"
                placeholder="请输入脚本名称"
                type="textarea"
                :rows="2"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="8"
              :label="`查找正则 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].findRegex`"
            >
              <n-input
                v-model:value="formData.extensions.regex_scripts[index].findRegex"
                placeholder="请输入查找正则表达式"
                type="textarea"
                :rows="2"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="8"
              :label="`替换字符串 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].replaceString`"
            >
              <n-input
                v-model:value="formData.extensions.regex_scripts[index].replaceString"
                placeholder="请输入替换字符串"
                type="textarea"
                :rows="2"
              />
            </n-form-item-gi>
          </n-grid>

          <!-- 裁剪字符串：24 -->
          <n-form-item
            :label="`裁剪字符串 ${index + 1}`"
            :path="`extensions.regex_scripts[${index}].trimStrings`"
          >
            <n-dynamic-input
              v-model:value="formData.extensions.regex_scripts[index].trimStrings"
              placeholder="请输入裁剪字符串"
              :on-create="() => ''"
            />
          </n-form-item>

          <!-- 放置位置、禁用状态、仅 Markdown：8*3 -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="8"
              :label="`放置位置 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].placement`"
            >
              <n-dynamic-tags
                v-model:value="formData.extensions.regex_scripts[index].placement"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="8"
              :label="`禁用状态 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].disabled`"
            >
              <n-switch v-model:value="formData.extensions.regex_scripts[index].disabled" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="8"
              :label="`仅 Markdown ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].markdownOnly`"
            >
              <n-switch
                v-model:value="formData.extensions.regex_scripts[index].markdownOnly"
              />
            </n-form-item-gi>
          </n-grid>

          <!-- 仅提示、编辑时运行、替换正则类型：8*3 -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="8"
              :label="`仅提示 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].promptOnly`"
            >
              <n-switch v-model:value="formData.extensions.regex_scripts[index].promptOnly" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="8"
              :label="`编辑时运行 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].runOnEdit`"
            >
              <n-switch v-model:value="formData.extensions.regex_scripts[index].runOnEdit" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="8"
              :label="`替换正则类型 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].substituteRegex`"
            >
              <n-input-number
                v-model:value="formData.extensions.regex_scripts[index].substituteRegex"
                :min="0"
                placeholder="请输入替换正则类型"
              />
            </n-form-item-gi>
          </n-grid>

          <!-- 最小深度、最大深度：12*2 -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="12"
              :label="`最小深度 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].minDepth`"
            >
              <n-input-number
                v-model:value="formData.extensions.regex_scripts[index].minDepth"
                placeholder="请输入最小深度 (可选)"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="12"
              :label="`最大深度 ${index + 1}`"
              :path="`extensions.regex_scripts[${index}].maxDepth`"
            >
              <n-input-number
                v-model:value="formData.extensions.regex_scripts[index].maxDepth"
                placeholder="请输入最大深度 (可选)"
              />
            </n-form-item-gi>
          </n-grid>
        </n-space>
      </n-tab-pane>
    </n-tabs>
  </n-form-item>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 定义 props
const props = defineProps<{
  formData: any
}>()

// 当前选中的正则脚本标签页
const currentRegexScriptTab = ref<string>('')

// 生成 UUID 的辅助函数
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

// 计算属性：控制添加按钮状态
const addable = computed(() => {
  return {
    disabled: props.formData.extensions.regex_scripts?.length >= 10,
  }
})

// 计算属性：控制关闭按钮状态
const closable = computed(() => {
  return props.formData.extensions.regex_scripts?.length > 1
})

// 处理添加标签页事件
const handleAdd = () => {
  const newScript = {
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
  }

  if (!props.formData.extensions.regex_scripts) {
    props.formData.extensions.regex_scripts = []
  }

  props.formData.extensions.regex_scripts.push(newScript)
  // 切换到新添加的脚本标签页
  currentRegexScriptTab.value = newScript.id
}

// 处理关闭标签页事件
const handleClose = (scriptId: string) => {
  const scripts = props.formData.extensions.regex_scripts
  const nameIndex = scripts.findIndex((script: any) => script.id === scriptId)
  if (!~nameIndex) return

  scripts.splice(nameIndex, 1)

  // 如果关闭的是当前选中的标签页，切换到相邻的标签页
  if (currentRegexScriptTab.value === scriptId) {
    currentRegexScriptTab.value = scripts[Math.min(nameIndex, scripts.length - 1)]?.id || ''
  }
}

// 将字符串类型的extensions.talkativeness转换为数字类型供InputNumber使用
const extensionsTalkativenessNumber = computed(() => {
  const stringValue = props.formData.extensions?.talkativeness
  if (typeof stringValue === 'string') {
    return parseFloat(stringValue) || 0.5
  }
  return stringValue || 0.5
})

// 将数字类型的talkativeness转换回字符串类型保存到formData.extensions
const updateExtensionsTalkativeness = (value: number | null) => {
  if (value === null) {
    props.formData.extensions.talkativeness = '0.5'
  } else {
    props.formData.extensions.talkativeness = value.toString()
  }
}
</script>

<style scoped>
/* 可以添加一些特定于此组件的样式 */
</style>
