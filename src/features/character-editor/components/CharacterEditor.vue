<template>
  <n-tabs type="line" animated>
    <n-tab-pane name="basic" tab="基础信息">
      <n-form
        ref="basicFormRef"
        :model="characterData"
        :rules="basicFormRules"
        label-placement="top"
        class="editor-form"
      >
        <n-space vertical size="large">
          <!-- 核心信息 -->
          <n-card title="核心信息" :bordered="false" header-style="padding-bottom: 8px;">
            <n-grid :cols="12" :x-gap="24">
              <n-form-item-gi :span="4" label="名称" path="name">
                <n-input v-model:value="characterData.name" placeholder="角色名称" />
              </n-form-item-gi>
              <n-form-item-gi :span="8" label="标签" path="tags">
                <n-dynamic-tags v-model:value="characterData.tags" />
              </n-form-item-gi>
              <n-form-item-gi :span="12" label="(角色)描述" path="description">
                <n-input
                  v-model:value="characterData.description"
                  type="textarea"
                  :autosize="{ minRows: 3 }"
                  placeholder="角色的核心描述，会极大地影响其行为。"
                />
              </n-form-item-gi>
              <n-form-item-gi :span="12" label="开场白" path="first_mes">
                <n-input
                  v-model:value="characterData.first_mes"
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
                  v-model:value="characterData.personality"
                  type="textarea"
                  :autosize="{ minRows: 2 }"
                  placeholder="角色的性格特点。"
                />
              </n-form-item-gi>
              <n-form-item-gi :span="6" label="场景" path="scenario">
                <n-input
                  v-model:value="characterData.scenario"
                  type="textarea"
                  :autosize="{ minRows: 2 }"
                  placeholder="故事发生的背景或环境。"
                />
              </n-form-item-gi>
              <n-form-item-gi :span="12" label="对话示例" path="mes_example">
                <n-input
                  v-model:value="characterData.mes_example"
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
                <n-input v-model:value="characterData.avatar" placeholder="avatar.png" />
              </n-form-item-gi>
              <n-form-item-gi :span="4" label="聊天记录" path="chat">
                <n-input v-model:value="characterData.chat" placeholder="char_chat.jsonl" />
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
                <n-input v-model:value="characterData.create_date" />
              </n-form-item-gi>
              <n-form-item-gi :span="4" label="规格" path="spec">
                <n-input v-model:value="characterData.spec" readonly />
              </n-form-item-gi>
              <n-form-item-gi :span="4" label="规格版本" path="spec_version">
                <n-input v-model:value="characterData.spec_version" readonly />
              </n-form-item-gi>
              <n-form-item-gi :span="4" label="收藏" path="fav">
                <n-switch v-model:value="characterData.fav" />
              </n-form-item-gi>
              <n-form-item-gi :span="8" label="创建者备注" path="creatorcomment">
                <n-input
                  v-model:value="characterData.creatorcomment"
                  type="textarea"
                  :autosize="{ minRows: 1 }"
                />
              </n-form-item-gi>
            </n-grid>
          </n-card>
        </n-space>
      </n-form>
    </n-tab-pane>
    <n-tab-pane name="data" tab="详细数据">
      <n-form
        ref="dataFormRef"
        :model="characterData.data"
        label-placement="top"
        class="editor-form"
      >
        <n-space vertical size="large">
          <!-- 基础数据 -->
          <n-card title="基础数据" :bordered="false" header-style="padding-bottom: 8px;">
            <n-space vertical size="large">
              <!-- 元数据 -->
              <n-h4 prefix="bar">元数据</n-h4>
              <n-grid :cols="12" :x-gap="24" :y-gap="8">
                <n-form-item-gi :span="4" label="角色卡名称" path="name">
                  <n-input v-model:value="characterData.data.name" placeholder="请输入角色卡名称" />
                </n-form-item-gi>
                <n-form-item-gi :span="4" label="创作者" path="creator">
                  <n-input v-model:value="characterData.data.creator" placeholder="请输入创建者" />
                </n-form-item-gi>
                <n-form-item-gi :span="4" label="角色卡版本号" path="character_version">
                  <n-input v-model:value="characterData.data.character_version" placeholder="请输入角色版本" />
                </n-form-item-gi>
                <n-form-item-gi :span="12" label="标签" path="tags">
                  <n-dynamic-tags v-model:value="characterData.data.tags">
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
                  <n-input v-model:value="characterData.data.description" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
                <n-form-item-gi :span="6" label="角色性格" path="personality">
                  <n-input v-model:value="characterData.data.personality" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
                <n-form-item-gi :span="6" label="角色场景" path="scenario">
                  <n-input v-model:value="characterData.data.scenario" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
                <n-form-item-gi :span="12" label="角色对话示例" path="mes_example">
                  <n-input v-model:value="characterData.data.mes_example" type="textarea" :autosize="{ minRows: 3 }" />
                </n-form-item-gi>
              </n-grid>
              
              <!-- 问候语 -->
              <n-h4 prefix="bar">问候语</n-h4>
              <n-grid :cols="12" :x-gap="24" :y-gap="8">
                <n-form-item-gi :span="12" label="角色开场白" path="first_mes">
                  <n-input v-model:value="characterData.data.first_mes" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
                <n-form-item-gi :span="12" label="备用开场白" path="alternate_greetings">
                  <n-dynamic-input
                    v-model:value="characterData.data.alternate_greetings"
                    placeholder="请输入备用开场白"
                    :on-create="() => ''"
                  />
                </n-form-item-gi>
              </n-grid>

              <!-- 高级设定 -->
              <n-h4 prefix="bar">高级设定</n-h4>
              <n-grid :cols="12" :x-gap="24" :y-gap="8">
                <n-form-item-gi :span="12" label="创作者备注" path="creator_notes">
                  <n-input v-model:value="characterData.data.creator_notes" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
                <n-form-item-gi :span="12" label="系统提示词" path="system_prompt">
                  <n-input v-model:value="characterData.data.system_prompt" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
                <n-form-item-gi :span="12" label="聊天后指令（又称后置指令）" path="post_history_instructions">
                  <n-input v-model:value="characterData.data.post_history_instructions" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
              </n-grid>
            </n-space>
          </n-card>

          <n-divider />

          <!-- 拓展用字段 -->
          <n-card title="拓展用字段" :bordered="false" header-style="padding-bottom: 8px;">
            <n-space v-if="characterData.data.extensions" vertical size="large">
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
                  <n-input v-model:value="characterData.data.extensions.world" placeholder="世界名称" />
                </n-form-item-gi>
                <n-form-item-gi :span="3" label="收藏" path="extensions.fav">
                  <n-switch v-model:value="characterData.data.extensions.fav" />
                </n-form-item-gi>
              </n-grid>

              <!-- 深度提示 -->
              <n-h4 prefix="bar">深度提示</n-h4>
              <n-grid :cols="12" :x-gap="24" :y-gap="8">
                <n-form-item-gi :span="3" label="深度" path="extensions.depth_prompt.depth">
                  <n-input-number v-model:value="characterData.data.extensions.depth_prompt.depth" :min="1" :max="10" />
                </n-form-item-gi>
                <n-form-item-gi :span="9" label="角色" path="extensions.depth_prompt.role">
                  <n-input v-model:value="characterData.data.extensions.depth_prompt.role" placeholder="角色" />
                </n-form-item-gi>
                <n-form-item-gi :span="12" label="提示内容" path="extensions.depth_prompt.prompt">
                  <n-input v-model:value="characterData.data.extensions.depth_prompt.prompt" type="textarea" :autosize="{ minRows: 2 }" />
                </n-form-item-gi>
              </n-grid>

              <!-- 正则脚本 -->
              <n-h4 prefix="bar">正则脚本</n-h4>
              <n-dynamic-input
                v-model:value="characterData.data.extensions.regex_scripts"
                :on-create="handleCreateRegexScript"
                v-if="characterData.data.extensions"
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
          </n-card>

          <n-divider />

          <!-- 角色书 / 世界观设定 -->
          <n-card title="角色书 / 世界观设定" :bordered="false" header-style="padding-bottom: 8px;">
            <n-space v-if="characterData.data.character_book" vertical size="large">
              <n-form-item label="世界书名称" path="character_book.name">
                <n-input v-model:value="characterData.data.character_book.name" placeholder="请输入世界书名称" />
              </n-form-item>

              <n-h4 prefix="bar">条目</n-h4>
              <n-dynamic-input
                v-model:value="characterData.data.character_book.entries"
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
          </n-card>
        </n-space>
      </n-form>
    </n-tab-pane>
  </n-tabs>
  <n-button @click="saveData" type="primary" block style="margin-top: 24px;">保存全部更改</n-button>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { FormInst, FormRules } from 'naive-ui';
import { useDataManager } from '@/store/dataManager';
import { storeToRefs } from 'pinia';
import { Add as AddIcon } from '@vicons/ionicons5';
import { 
  NForm, NSpace, NCard, NDivider, NGrid, NFormItemGi, NInput, NDynamicTags, NInputNumber, NSwitch, 
  NH4, NDynamicInput, NCollapse, NCollapseItem, NSelect, NFormItem, NButton, NIcon, NTabs, NTabPane
} from 'naive-ui';

const dataManager = useDataManager();
const { characterData } = storeToRefs(dataManager);

const basicFormRef = ref<FormInst | null>(null);
const dataFormRef = ref<FormInst | null>(null);

// --- Basic Editor Logic ---
const basicFormRules: FormRules = {
  name: { required: true, message: '请输入角色名称', trigger: 'blur' },
  description: { required: true, message: '请输入角色描述', trigger: 'blur' },
};

const talkativenessNumber = computed(() => {
  const stringValue = characterData.value.talkativeness;
  return typeof stringValue === 'string' ? parseFloat(stringValue) || 0.5 : stringValue || 0.5;
});

const updateTalkativeness = (value: number | null) => {
  characterData.value.talkativeness = value === null ? '0.5' : value.toString();
};

// --- Data Editor Logic ---
onMounted(() => {
  if (!characterData.value.data.extensions) {
    characterData.value.data.extensions = {
      talkativeness: '0.5',
      fav: false,
      world: '',
      depth_prompt: {
        prompt: '',
        depth: 1,
        role: ''
      },
      regex_scripts: []
    };
  }

  if (!characterData.value.data.character_book) {
    characterData.value.data.character_book = {
      name: '',
      entries: []
    };
  }
});

const extensionsTalkativenessNumber = computed(() => {
  const stringValue = characterData.value.data.extensions?.talkativeness;
  return typeof stringValue === 'string' ? parseFloat(stringValue) || 0.5 : stringValue || 0.5;
});

const updateExtensionsTalkativeness = (value: number | null) => {
  if (characterData.value.data.extensions) {
    characterData.value.data.extensions.talkativeness = value === null ? '0.5' : value.toString();
  }
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

// --- Unified Save ---
const saveData = () => {
  dataManager.setFullData(JSON.parse(JSON.stringify(characterData.value)));
  // Optionally, you can add validation for both forms here
  // basicFormRef.value?.validate(...)
  // dataFormRef.value?.validate(...)
};
</script>

<style scoped>
.editor-form {
  padding: 8px;
}
</style>
