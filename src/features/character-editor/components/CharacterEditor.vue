<template>
  <div class="editor-content">
    <keep-alive>
      <component :is="activeComponent" />
    </keep-alive>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import CharacterBasicEditor from './CharacterBasicEditor.vue';
import CharacterDataEditor from './CharacterDataEditor.vue';

const props = defineProps({
  activeTab: {
    type: String,
    required: true,
    default: 'basic'
  }
});

const activeComponent = computed(() => {
  return props.activeTab === 'basic' ? CharacterBasicEditor : CharacterDataEditor;
});
</script>

<style scoped>
.editor-content {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  box-sizing: border-box;
}
</style>
