<template>
  <div>
    <h2>设置</h2>
    <n-split direction="horizontal" style="height: 80vh">
      <template #1>
        <n-card title="基本设置">
          <n-form>
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
            <n-checkbox v-model:checked="settings.wrap_in_quotes">用引号包裹</n-checkbox>
            <n-checkbox v-model:checked="settings.max_context_unlocked">解锁最大上下文</n-checkbox>
            <n-checkbox v-model:checked="settings.stream_openai">流式传输</n-checkbox>
            <n-checkbox v-model:checked="settings.show_external_models">Show External Models</n-checkbox>
            <n-checkbox v-model:checked="settings.claude_use_sysprompt">Claude使用系统提示</n-checkbox>
            <n-checkbox v-model:checked="settings.squash_system_messages">压缩系统消息</n-checkbox>
            <n-checkbox v-model:checked="settings.image_inlining">发送图片</n-checkbox>
            <n-checkbox v-model:checked="settings.bypass_status_check">Bypass Status Check</n-checkbox>
            <n-checkbox v-model:checked="settings.continue_prefill">Continue Prefill</n-checkbox>
            <n-form-item label="Bias Preset Selected">
              <n-select v-model:value="settings.bias_preset_selected" :options="biasPresetOptions" />
            </n-form-item>
            <n-form-item label="Names Behavior">
              <n-input-number v-model:value="settings.names_behavior" />
            </n-form-item>
            <n-form-item label="N">
              <n-input-number v-model:value="settings.n" />
            </n-form-item>
          </n-form>
        </n-card>
      </template>
      <template #2>
        <n-card title="文本设置">
          <n-form>
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
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';

const biasPresetOptions = [
  { label: 'Default (none)', value: 'Default (none)' },
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
];

const props = defineProps<{
  settings: any;
}>();

const emit = defineEmits(['update:settings']);

const settings = reactive(props.settings);

watch(() => props.settings, (newVal) => {
  Object.assign(settings, newVal);
});

watch(settings, (newVal) => {
  emit('update:settings', newVal);
}, { deep: true });
</script>
