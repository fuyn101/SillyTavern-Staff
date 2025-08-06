<template>
  <div class="home-view">
    <h1>功能选择</h1>
    <p style="margin-bottom: 20px; color: #888;">应用的首页，作为功能选择的入口，提供导航到角色编辑器、预设对比编辑器和文件管理器。</p>
    <n-space vertical :size="20" style="width: 400px;">
      <n-card hoverable @click="goToEditor" class="action-card">
        <template #header>
          <n-h3 style="margin: 0;">角色编辑器</n-h3>
        </template>
        在这里，您可以从头开始创建新的人物卡，或加载并编辑现有的人物卡。调整角色的基本信息、对话示例、角色设定等。
      </n-card>
      <n-card hoverable @click="goToTwoPageEditor" class="action-card">
        <template #header>
          <n-h3 style="margin: 0;">预设对比编辑器</n-h3>
        </template>
        这个工具允许您并排查看和编辑两个不同的预设或角色卡。方便您进行内容比对、迁移和合并。
      </n-card>
      <n-card hoverable @click="goToFileManager" class="action-card">
        <template #header>
          <n-h3 style="margin: 0;">文件管理器</n-h3>
        </template>
        管理您本地存储的角色卡和预设文件。您可以进行文件的导入、导出、删除等操作。
      </n-card>
    </n-space>
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
  padding-top: 40px;
  box-sizing: border-box;
  height: 100%;
}

.action-card {
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  border-color: #18a058;
  transform: translateY(-2px);
}
</style>
