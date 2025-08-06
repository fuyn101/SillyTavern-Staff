<script setup lang="ts">
import { NConfigProvider, NMessageProvider, NNotificationProvider, NDialogProvider, NLoadingBarProvider, NSpace, NButton, NLayout, NLayoutHeader, NLayoutContent } from "naive-ui";
import { useRouter } from 'vue-router';
import { useThemeStore } from './store/theme';

const router = useRouter();
const themeStore = useThemeStore();
</script>

<template>
  <n-config-provider :theme="themeStore.theme">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <n-loading-bar-provider>
            <n-layout >
              <n-layout-header >
                <n-space  justify="center">
                  <n-button @click="router.push('/')">主页</n-button>
                  <n-button @click="router.push('/editor')">编辑器</n-button>
                  <n-button @click="router.push('/two-page-editor')">预设对比编辑器</n-button>
                  <n-button @click="router.push('/file-manager')">文件管理</n-button>
                  <n-button @click="themeStore.toggleTheme">切换主题</n-button>
                </n-space>
              </n-layout-header>
              <n-layout-content >
                <router-view style="height: 90vh;"/>
              </n-layout-content>
            </n-layout>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
</style>
