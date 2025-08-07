<template>
  <n-layout style="height: 100vh">
    <n-layout-header bordered style="padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;">
      <n-h3 style="margin: 0;">预设编辑器 ({{ side }})</n-h3>
      <n-space>
        <n-button @click="handleOpenFile">打开</n-button>
        <n-button @click="handleSaveFile">保存</n-button>
        <n-button @click="handleSaveFileAs">另存为</n-button>
        <n-button @click="loadDefaultPreset">加载默认预设</n-button>
      </n-space>
    </n-layout-header>

    <n-layout-content >
      <n-tabs type="line" animated style="height: 100%" ">
        <!-- PromptsTab.vue content start -->
        <n-tab-pane name="prompts" style="height: 100vh" "  tab="提示词管理">
          <n-split direction="horizontal" style="height: 100%">
            <template #1>
              <n-card title="提示词列表" :bordered="false" size="small" style="height: 100%; display: flex; flex-direction: column;" content-style="flex: 1; overflow-y: auto;">
                <div class="list-container" v-drag-list="{ list: prompts, key: 'identifier', dragItemClass: 'drag-item', dragHandleClass: 'drag-handle' }" @drag-end="handleDragEnd">
                  <div
                    v-for="(prompt, index) in prompts"
                    :key="prompt.identifier"
                    :data-id="prompt.identifier"
                    @click="selectPrompt(index)"
                    class="drag-item list-item-imitation"
                    :class="{ 'active-item': selectedIndex === index }"
                  >
                    <span class="drag-handle">⋮⋮</span>
                    <span>{{ prompt.name }}</span>
                  </div>
                </div>
                <template #footer>
                  <n-space>
                    <n-button @click="addPrompt" type="primary" size="small">添加</n-button>
                    <n-button @click="deletePrompt" type="error" size="small">删除</n-button>
                  </n-space>
                </template>
              </n-card>
            </template>
            <template #2>
              <n-card title="提示词详情" :bordered="false" size="small" style="height: 100%">
                <n-tabs type="line" animated>
                  <n-tab-pane name="editor" tab="编辑器">
                    <n-form v-if="selectedIndex !== -1" label-placement="top">
                      <n-form-item label="提示词名称">
                        <n-input v-model:value="selectedPrompt.name" />
                      </n-form-item>
                      <n-grid :cols="2" :x-gap="12">
                        <n-gi>
                          <n-form-item>
                            <n-checkbox v-model:checked="selectedPrompt.system_prompt">是否为标准模版默认提示词</n-checkbox>
                          </n-form-item>
                          <n-form-item label="Role">
                            <n-select v-model:value="selectedPrompt.role" :options="roleOptions" />
                          </n-form-item>
                          <n-form-item label="Identifier">
                            <n-input v-model:value="selectedPrompt.identifier" />
                          </n-form-item>
                          <n-form-item>
                            <n-checkbox v-model:checked="selectedPrompt.add_to_order">是否在列表里</n-checkbox>
                          </n-form-item>
                          <n-form-item>
                            <n-checkbox v-model:checked="selectedPrompt.enabled">是否在列表里开启</n-checkbox>
                          </n-form-item>
                          <n-form-item>
                            <n-checkbox v-model:checked="selectedPrompt.marker">是否是图钉提示词</n-checkbox>
                          </n-form-item>
                        </n-gi>
                        <n-gi>
                          <n-form-item label="注入位置">
                            <n-select v-model:value="selectedPrompt.injection_position" :options="injectionPositionOptions" />
                          </n-form-item>
                          <n-form-item label="注入深度（1时使用）">
                            <n-input-number v-model:value="selectedPrompt.injection_depth" />
                          </n-form-item>
                          <n-form-item label="注入顺序（1时使用）">
                            <n-input-number v-model:value="selectedPrompt.injection_order" />
                          </n-form-item>
                          <n-form-item>
                            <n-checkbox v-model:checked="selectedPrompt.forbid_overrides">Forbid Overrides</n-checkbox>
                          </n-form-item>
                        </n-gi>
                      </n-grid>
                      <n-form-item label="Content">
                        <n-input type="textarea" v-model:value="selectedPrompt.content" :autosize="{ minRows: 6 }" />
                      </n-form-item>
                      <n-button @click="savePrompt" type="primary" block>保存提示词</n-button>
                    </n-form>
                     <n-empty v-else description="请在左侧选择一个提示词进行编辑" style="margin-top: 48px;" />
                  </n-tab-pane>
                  <n-tab-pane name="variables" tab="变量信息">
                    <n-input v-model:value="variableFilter" placeholder="筛选变量" />
                    <n-data-table :columns="variableColumns" :data="filteredVariables" />
                  </n-tab-pane>
                </n-tabs>
              </n-card>
            </template>
          </n-split>
        </n-tab-pane>
        <!-- PromptsTab.vue content end -->

        <!-- PromptSettings.vue content start -->
        <n-tab-pane name="settings" tab="设置">
          <n-split direction="horizontal" style="height: 100%">
            <template #1>
              <n-card title="基本设置" :bordered="false" size="small">
                <n-form label-placement="left" label-width="auto">
                  <n-form-item label="温度">
                    <n-slider v-model:value="settings.temperature" :min="0" :max="2" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="频率惩罚">
                    <n-slider v-model:value="settings.frequency_penalty" :min="-2" :max="2" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="存在惩罚">
                    <n-slider v-model:value="settings.presence_penalty" :min="-2" :max="2" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="Top P">
                    <n-slider v-model:value="settings.top_p" :min="0" :max="1" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="Top K">
                    <n-input-number v-model:value="settings.top_k" />
                  </n-form-item>
                  <n-form-item label="Top A">
                    <n-slider v-model:value="settings.top_a" :min="0" :max="1" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="Min P">
                    <n-slider v-model:value="settings.min_p" :min="0" :max="1" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="重复惩罚">
                    <n-slider v-model:value="settings.repetition_penalty" :min="0" :max="2" :step="0.01" />
                  </n-form-item>
                  <n-form-item label="最大上下文">
                    <n-input-number v-model:value="settings.openai_max_context" />
                  </n-form-item>
                  <n-form-item label="最大输出内容">
                    <n-input-number v-model:value="settings.openai_max_tokens" />
                  </n-form-item>
                  <n-form-item label="种子">
                    <n-input-number v-model:value="settings.seed" />
                  </n-form-item>
                  <n-form-item label="Bias Preset Selected">
                    <n-select v-model:value="settings.bias_preset_selected" :options="biasPresetOptions" />
                  </n-form-item>
                  <n-form-item label="Names Behavior">
                    <n-input-number v-model:value="settings.names_behavior" />
                  </n-form-item>
                  <n-form-item label="N">
                    <n-input-number v-model:value="settings.n" />
                  </n-form-item>
                  <n-space item-style="display: flex;">
                    <n-checkbox v-model:checked="settings.wrap_in_quotes">用引号包裹</n-checkbox>
                    <n-checkbox v-model:checked="settings.max_context_unlocked">解锁最大上下文</n-checkbox>
                    <n-checkbox v-model:checked="settings.stream_openai">流式传输</n-checkbox>
                    <n-checkbox v-model:checked="settings.show_external_models">Show External Models</n-checkbox>
                    <n-checkbox v-model:checked="settings.claude_use_sysprompt">Claude使用系统提示</n-checkbox>
                    <n-checkbox v-model:checked="settings.squash_system_messages">压缩系统消息</n-checkbox>
                    <n-checkbox v-model:checked="settings.image_inlining">发送图片</n-checkbox>
                    <n-checkbox v-model:checked="settings.bypass_status_check">Bypass Status Check</n-checkbox>
                    <n-checkbox v-model:checked="settings.continue_prefill">Continue Prefill</n-checkbox>
                  </n-space>
                </n-form>
              </n-card>
            </template>
            <template #2>
              <n-card title="文本设置" :bordered="false" size="small">
                <n-form label-placement="top">
                  <n-form-item label="Send If Empty">
                    <n-input v-model:value="settings.send_if_empty" />
                  </n-form-item>
                  <n-form-item label="Assistant Prefill">
                    <n-input v-model:value="settings.assistant_prefill" />
                  </n-form-item>
                  <n-form-item label="Assistant Impersonation">
                    <n-input v-model:value="settings.assistant_impersonation" />
                  </n-form-item>
                  <n-form-item label="Continue Postfix">
                    <n-input v-model:value="settings.continue_postfix" />
                  </n-form-item>
                  <n-form-item label="Impersonation Prompt">
                    <n-input type="textarea" v-model:value="settings.impersonation_prompt" :rows="4" />
                  </n-form-item>
                  <n-form-item label="New Chat Prompt">
                    <n-input type="textarea" v-model:value="settings.new_chat_prompt" :rows="4" />
                  </n-form-item>
                  <n-form-item label="New Group Chat Prompt">
                    <n-input type="textarea" v-model:value="settings.new_group_chat_prompt" :rows="4" />
                  </n-form-item>
                  <n-form-item label="New Example Chat Prompt">
                    <n-input type="textarea" v-model:value="settings.new_example_chat_prompt" :rows="4" />
                  </n-form-item>
                  <n-form-item label="Continue Nudge Prompt">
                    <n-input type="textarea" v-model:value="settings.continue_nudge_prompt" :rows="4" />
                  </n-form-item>
                  <n-form-item label="Group Nudge Prompt">
                    <n-input type="textarea" v-model:value="settings.group_nudge_prompt" :rows="4" />
                  </n-form-item>
                </n-form>
              </n-card>
            </template>
          </n-split>
        </n-tab-pane>
        <!-- PromptSettings.vue content end -->
      </n-tabs>
    </n-layout-content>
  </n-layout>
</template>

<script setup lang="ts">
import { reactive, watch, ref, computed } from 'vue';
import { 
  NLayout, NLayoutContent, NLayoutHeader, NTabs, NTabPane, NButton, NCard, NSplit, NForm, NFormItem, NInput, NCheckbox, NSelect, NInputNumber, NSlider, NGrid, NGi, NDataTable, NH3, NSpace, NEmpty
} from 'naive-ui';
import { useFileSystem } from '@/composables/useFileSystem';
import defaultPreset from '@/assets/Default prompt.json';
import { useDataManager } from '@/store/dataManager';
import { v4 as uuidv4 } from 'uuid';
import { vDragList } from 'vue3-drag-directive';

// --- Component Props ---
const props = defineProps<{
  side: 'left' | 'right';
}>();

// --- File System and Data Management ---
const { openFile, saveFile, saveFileAs } = useFileSystem();
const dataManager = useDataManager();
const jsonData = props.side === 'left' ? dataManager.presetEditorLeft : dataManager.presetEditorRight;

const filePickerOptions: FilePickerOptions = {
  types: [
    {
      description: 'JSON Files',
      accept: { 'application/json': ['.json'] },
    },
  ],
};

async function handleOpenFile() {
  const data = await openFile(filePickerOptions);
  if (data) {
    dataManager.updatePresetEditorData(props.side, data);
  }
}

function handleSaveFile() {
  saveFile(jsonData);
}

function handleSaveFileAs() {
  saveFileAs(jsonData, filePickerOptions);
}

function loadDefaultPreset() {
  dataManager.updatePresetEditorData(props.side, defaultPreset);
}

watch(jsonData, (newData) => {
  dataManager.updatePresetEditorData(props.side, newData);
}, { deep: true });


// --- PromptsTab Logic ---
const prompts = ref<any[]>(jsonData.prompts);
const selectedPrompt = reactive<any>({});
let selectedIndex = ref(-1);

const roleOptions = [
  { label: 'system', value: 'system' },
  { label: 'assistant', value: 'assistant' },
  { label: 'user', value: 'user' },
];

const injectionPositionOptions = [
  { label: '0 (相对)', value: 0 },
  { label: '1 (深度)', value: 1 },
];

watch(() => jsonData.prompts, (newVal) => {
  prompts.value = newVal;
  if (selectedIndex.value >= newVal.length) {
    selectPrompt(newVal.length - 1);
  }
});

const variableFilter = ref('');

const variableColumns = [
  { title: '所在提示词', key: 'promptName' },
  { title: '变量名', key: 'varName' },
  { title: '类型', key: 'varType' },
  { title: '变量内容', key: 'varValue' },
];

const allVariables = computed(() => {
  const variables: any[] = [];
  prompts.value.forEach(prompt => {
    const content = prompt.content || '';
    const setvarMatches = [...content.matchAll(/{{setvar::(.*?)::(.*?)}}/g)];
    setvarMatches.forEach(match => {
      variables.push({
        promptName: prompt.name,
        varName: match[1],
        varType: 'setvar',
        varValue: match[2],
        promptIdentifier: prompt.identifier,
      });
    });

    const getvarMatches = [...content.matchAll(/{{getvar::(.*?)}}/g)];
    getvarMatches.forEach(match => {
      variables.push({
        promptName: prompt.name,
        varName: match[1],
        varType: 'getvar',
        varValue: '',
        promptIdentifier: prompt.identifier,
      });
    });
  });
  return variables;
});

const filteredVariables = computed(() => {
  if (!variableFilter.value) {
    return allVariables.value;
  }
  return allVariables.value.filter(variable =>
    variable.varName.toLowerCase().includes(variableFilter.value.toLowerCase())
  );
});

function selectPrompt(index: number) {
  if (index >= 0 && index < prompts.value.length) {
    selectedIndex.value = index;
    Object.assign(selectedPrompt, prompts.value[index]);
  } else {
    selectedIndex.value = -1;
    Object.keys(selectedPrompt).forEach(key => delete selectedPrompt[key]);
  }
}

function addPrompt() {
  const newPrompt = {
    name: "New Prompt",
    system_prompt: false,
    role: "user",
    content: "",
    identifier: uuidv4(),
    add_to_order: true,
    enabled: true,
    marker: false,
    injection_position: 0,
    injection_depth: 4,
    injection_order: 100,
    forbid_overrides: false,
  };
  prompts.value.push(newPrompt);
  selectPrompt(prompts.value.length - 1);
}

function deletePrompt() {
  if (selectedIndex.value !== -1) {
    prompts.value.splice(selectedIndex.value, 1);
    if (prompts.value.length > 0) {
      selectPrompt(Math.max(0, selectedIndex.value - 1));
    } else {
      selectPrompt(-1);
    }
  }
}

function savePrompt() {
  if (selectedIndex.value !== -1) {
    prompts.value[selectedIndex.value] = { ...selectedPrompt };
  }
}

function handleDragEnd(event: any) {
  console.log('Drag operation finished:', event);
}

// --- PromptSettings Logic ---
const settings = reactive(jsonData);

const biasPresetOptions = [
  { label: 'Default (none)', value: 'Default (none)' },
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
];

watch(() => jsonData, (newVal) => {
  Object.assign(settings, newVal);
}, { deep: true });

</script>

<style scoped>
.list-container {
  border: 1px solid rgb(224, 224, 230);
  border-radius: 3px;
  overflow-y: auto;
}

.list-item-imitation {
  padding: 8px 12px;
  border-bottom: 1px solid rgb(224, 224, 230);
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.list-item-imitation:last-child {
  border-bottom: none;
}

.list-item-imitation:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.active-item {
  background-color: #e8f4ff;
  color: #2d8cf0;
}

.drag-handle {
  cursor: grab;
  margin-right: 10px;
  user-select: none;
}
</style>
