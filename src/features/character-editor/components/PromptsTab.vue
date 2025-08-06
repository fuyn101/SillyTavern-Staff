<template>
  <n-layout style="height: 100%">
    <n-layout-header style="padding: 12px 24px; font-weight: bold; font-size: 1.2em;">
      提示词管理
    </n-layout-header>
    <n-layout-content content-style="padding: 0 24px 24px; height: calc(100% - 120px);">
      <n-split direction="horizontal" style="height: 100%">
        <template #1>
          <n-card title="提示词列表" :content-style="{ flex: 1 }" :style="{ height: '100%', display: 'flex', flexDirection: 'column' }">
            <div class="list-container" v-drag-list="{ list: prompts, key: 'identifier', dragItemClass: 'drag-item', dragHandleClass: 'drag-handle' }" @drag-end="handleDragEnd">
              <div
                v-for="(prompt, index) in prompts"
                :key="prompt.identifier"
                :data-id="prompt.identifier"
                @click="selectPrompt(index)"
                class="drag-item list-item-imitation"
              >
                <span class="drag-handle">⋮⋮</span>
                <span>{{ prompt.name }}</span>
              </div>
            </div>
          </n-card>
        </template>
        <template #2>
          <n-tabs type="line" animated>
            <n-tab-pane name="editor" tab="编辑器">
              <n-card title="提示词详情">
                <n-form>
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
                    <n-input type="textarea" v-model:value="selectedPrompt.content" :rows="6" />
                  </n-form-item>
                </n-form>
              </n-card>
            </n-tab-pane>
            <n-tab-pane name="variables" tab="变量信息">
              <n-input v-model:value="variableFilter" placeholder="筛选变量" />
              <n-data-table :columns="variableColumns" :data="filteredVariables" />
            </n-tab-pane>
          </n-tabs>
        </template>
      </n-split>
    </n-layout-content>
    <n-layout-footer style="padding: 12px 24px; display: flex; justify-content: space-between;">
      <div>
        <n-button @click="addPrompt" type="primary">添加</n-button>
        <n-button @click="deletePrompt" type="error" style="margin-left: 8px;">删除</n-button>
      </div>
      <n-button @click="savePrompt" type="success">保存提示词</n-button>
    </n-layout-footer>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { vDragList } from 'vue3-drag-directive';

const roleOptions = [
  { label: 'system', value: 'system' },
  { label: 'assistant', value: 'assistant' },
  { label: 'user', value: 'user' },
];

const injectionPositionOptions = [
  { label: '0 (相对)', value: 0 },
  { label: '1 (深度)', value: 1 },
];

const props = defineProps<{
  prompts: any[];
}>();

const emit = defineEmits(['update:prompts']);

const prompts = ref<any[]>(props.prompts);
const selectedPrompt = reactive<any>({});
let selectedIndex = -1;

watch(() => props.prompts, (newVal) => {
  prompts.value = newVal;
});

watch(prompts, (newVal) => {
  emit('update:prompts', newVal);
}, { deep: true });

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
  selectedIndex = index;
  Object.assign(selectedPrompt, prompts.value[index]);
}

function addPrompt() {
  const newPrompt = {
    name: "New Prompt",
    system_prompt: false,
    role: "user",
    content: "",
    identifier: uuidv4(),
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
  if (selectedIndex !== -1) {
    prompts.value.splice(selectedIndex, 1);
    if (prompts.value.length > 0) {
      selectPrompt(0);
    } else {
      Object.keys(selectedPrompt).forEach(key => delete selectedPrompt[key]);
      selectedIndex = -1;
    }
  }
}

function savePrompt() {
  if (selectedIndex !== -1) {
    prompts.value[selectedIndex] = { ...selectedPrompt };
  }
}

function handleDragEnd(event: any) {
  // The directive mutates the array directly.
  // The watcher on 'prompts' will emit the update to the parent.
  console.log('Drag operation finished:', event);
}
</script>

<style scoped>
.list-container {
  border: 1px solid rgb(224, 224, 230);
  border-radius: 3px;
}

.list-item-imitation {
  padding: 12px;
  border-bottom: 1px solid rgb(224, 224, 230);
  transition: background-color 0.3s;
}

.list-item-imitation:last-child {
  border-bottom: none;
}

.list-item-imitation:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.drag-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.drag-handle {
  cursor: grab;
  margin-right: 10px;
  user-select: none;
}
</style>
