<template>
  <!-- 世界书 名称设置 -->
  <n-grid :cols="24" :x-gap="12" :y-gap="8">
    <n-form-item-gi :span="24" label="世界书 名称" path="character_book.name">
      <n-input
        v-model:value="formData.character_book.name"
        placeholder="请输入 世界书 名称"
        type="textarea"
        :rows="1"
      />
    </n-form-item-gi>
  </n-grid>

  <!-- 世界书 Entries Tabs -->
  <n-form-item label="条目">
    <n-tabs
      type="card"
      v-model:value="currentCharacterBookTab"
      :addable="characterBookAddable"
      :closable="characterBookClosable"
      tab-style="min-width: 80px;"
      @close="handleCharacterBookClose"
      @add="handleCharacterBookAdd"
    >
      <n-tab-pane
        v-for="(entry, index) in formData.character_book.entries"
        :key="entry.id"
        :name="entry.id.toString()"
        :tab="entry.comment || `条目 ${index + 1}`"
      >
        <n-space vertical :size="12">
          <!-- 注释和内容 -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="12"
              :label="`世界书条目名称 ${index + 1}`"
              :path="`character_book.entries[${index}].comment`"
            >
              <n-input
                v-model:value="formData.character_book.entries[index].comment"
                placeholder="请输入条目注释"
                type="textarea"
                :rows="1"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="12"
              :label="`世界书条目内容 ${index + 1}`"
              :path="`character_book.entries[${index}].content`"
            >
              <n-input
                v-model:value="formData.character_book.entries[index].content"
                type="textarea"
                :rows="3"
                placeholder="请输入条目内容"
              />
            </n-form-item-gi>
          </n-grid>

          <!-- 配置选项和位置顺序 -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="6"
              :label="`启用状态`"
              :path="`character_book.entries[${index}].enabled`"
            >
              <n-switch v-model:value="formData.character_book.entries[index].enabled" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`常量`"
              :path="`character_book.entries[${index}].constant`"
            >
              <n-switch v-model:value="formData.character_book.entries[index].constant" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`选择性`"
              :path="`character_book.entries[${index}].selective`"
            >
              <n-switch v-model:value="formData.character_book.entries[index].selective" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`使用正则`"
              :path="`character_book.entries[${index}].use_regex`"
            >
              <n-switch v-model:value="formData.character_book.entries[index].use_regex" />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`插入顺序`"
              :path="`character_book.entries[${index}].insertion_order`"
            >
              <n-input-number
                v-model:value="formData.character_book.entries[index].insertion_order"
                :min="0"
                :max="1000"
                placeholder="插入顺序"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`位置`"
              :path="`character_book.entries[${index}].position`"
            >
              <n-select
                v-model:value="formData.character_book.entries[index].position"
                :options="positionOptions"
                placeholder="选择位置"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`显示索引`"
              :path="`character_book.entries[${index}].extensions.display_index`"
            >
              <n-input-number
                v-model:value="
                  formData.character_book.entries[index].extensions.display_index
                "
                :min="0"
                placeholder="显示索引"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`触发概率%`"
              :path="`character_book.entries[${index}].extensions.probability`"
            >
              <n-input-number
                v-model:value="formData.character_book.entries[index].extensions.probability"
                :min="0"
                :max="100"
                placeholder="概率 (0-100)"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`扫描深度`"
              :path="`character_book.entries[${index}].extensions.depth`"
            >
              <n-input-number
                v-model:value="formData.character_book.entries[index].extensions.depth"
                :min="1"
                :max="10"
                placeholder="深度"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="6"
              :label="`角色`"
              :path="`character_book.entries[${index}].extensions.role`"
            >
              <n-input-number
                v-model:value="formData.character_book.entries[index].extensions.role"
                :min="0"
                placeholder="角色"
              />
            </n-form-item-gi>
          </n-grid>

          <!-- 关键词 -->
          <n-grid :cols="24" :x-gap="12" :y-gap="8">
            <n-form-item-gi
              :span="12"
              :label="`主要关键词`"
              :path="`character_book.entries[${index}].keys`"
            >
              <n-dynamic-tags
                v-model:value="formData.character_book.entries[index].keys"
                placeholder="添加主要关键词"
              />
            </n-form-item-gi>

            <n-form-item-gi
              :span="12"
              :label="`次要关键词`"
              :path="`character_book.entries[${index}].secondary_keys`"
            >
              <n-dynamic-tags
                v-model:value="formData.character_book.entries[index].secondary_keys"
                placeholder="添加次要关键词"
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

// 当前选中的 世界书 标签页
const currentCharacterBookTab = ref<string>('')

// 位置选项
const positionOptions = [
  { label: '角色前', value: 'before_char' },
  { label: '角色后', value: 'after_char' },
  { label: '对话示例前', value: 'before_example' },
  { label: '对话示例后', value: 'after_example' },
]

// 计算属性：控制 世界书 添加按钮状态
const characterBookAddable = computed(() => {
  return {
    disabled: props.formData.character_book?.entries?.length >= 50,
  }
})

// 计算属性：控制 世界书 关闭按钮状态
const characterBookClosable = computed(() => {
  return props.formData.character_book?.entries?.length > 1
})

// 处理 世界书 添加标签页事件
const handleCharacterBookAdd = () => {
  const newEntry = {
    id: Date.now(), // 使用时间戳作为 ID
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
      position: 1,
      exclude_recursion: false,
      display_index: 0,
      probability: 100,
      useProbability: true,
      depth: 4,
      selectiveLogic: 0,
      group: '',
      group_override: false,
      group_weight: 100,
      prevent_recursion: false,
      delay_until_recursion: false,
      scan_depth: null,
      match_whole_words: null,
      use_group_scoring: false,
      case_sensitive: null,
      automation_id: '',
      role: 0,
      vectorized: false,
      sticky: 0,
      cooldown: 0,
      delay: 0,
    },
  }

  if (!props.formData.character_book) {
    props.formData.character_book = {
      name: '',
      entries: [],
    }
  }

  if (!props.formData.character_book.entries) {
    props.formData.character_book.entries = []
  }

  props.formData.character_book.entries.push(newEntry)
  // 切换到新添加的条目标签页
  currentCharacterBookTab.value = newEntry.id.toString()
}

// 处理 世界书 关闭标签页事件
const handleCharacterBookClose = (entryId: string) => {
  const entries = props.formData.character_book.entries
  const entryIndex = entries.findIndex((entry: any) => entry.id.toString() === entryId)
  if (!~entryIndex) return

  entries.splice(entryIndex, 1)

  // 如果关闭的是当前选中的标签页，切换到相邻的标签页
  if (currentCharacterBookTab.value === entryId) {
    currentCharacterBookTab.value =
      entries[Math.min(entryIndex, entries.length - 1)]?.id.toString() || ''
  }
}
</script>

<style scoped>
/* 可以添加一些特定于此组件的样式 */
</style>
