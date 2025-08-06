<template>
  <div class="home-view">
    <h1>功能选择</h1>
    <n-button type="primary" @click="goToEditor">角色编辑器</n-button>
    <n-button type="primary" @click="goToTwoPageEditor" style="margin-top: 12px;">预设对比编辑器</n-button>
    <n-button type="primary" @click="goToFileManager" style="margin-top: 12px;">文件管理器</n-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

function goToEditor() {
  router.push('/editor');
}

function goToTwoPageEditor() {
  router.push('/two-page-editor');
}

function goToFileManager() {
  router.push('/file-manager');
}
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
