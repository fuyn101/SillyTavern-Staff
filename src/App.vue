<script setup lang="ts">
import { h, type Component } from 'vue';
import { 
  NConfigProvider, 
  NMessageProvider, 
  NNotificationProvider, 
  NDialogProvider, 
  NLoadingBarProvider, 
  NLayout, 
  NLayoutHeader, 
  NLayoutContent, 
  NLayoutSider, 
  NMenu, 
  NIcon, 
  NButton 
} from "naive-ui";
import { useRouter, RouterLink } from 'vue-router';
import { useThemeStore } from './store/theme';
import {
  HomeOutline as HomeIcon,
  CreateOutline as EditorIcon,
  GitCompareOutline as CompareIcon,
  FolderOpenOutline as FileManagerIcon
} from '@vicons/ionicons5';

const router = useRouter();
const themeStore = useThemeStore();

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

const menuOptions = [
  {
    label: () => h(RouterLink, { to: '/' }, { default: () => '主页' }),
    key: 'home',
    icon: renderIcon(HomeIcon)
  },
  {
    label: () => h(RouterLink, { to: '/editor' }, { default: () => '角色编辑器' }),
    key: 'editor',
    icon: renderIcon(EditorIcon)
  },
  {
    label: () => h(RouterLink, { to: '/two-page-editor' }, { default: () => '预设对比编辑器' }),
    key: 'two-page-editor',
    icon: renderIcon(CompareIcon)
  },
  {
    label: () => h(RouterLink, { to: '/file-manager' }, { default: () => '文件管理器' }),
    key: 'file-manager',
    icon: renderIcon(FileManagerIcon)
  }
];
</script>

<template>
  <n-config-provider :theme="themeStore.theme">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <n-loading-bar-provider>
            <n-layout style="height: 100vh">
              <n-layout-header style="height: 64px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;" bordered>
                <span style="font-size: 1.5rem; font-weight: bold;">SillyTavern Staff</span>
                <n-button @click="themeStore.toggleTheme">切换主题</n-button>
              </n-layout-header>
              <n-layout has-sider position="static">
                <n-layout-sider
                  bordered
                  collapse-mode="width"
                  :collapsed-width="64"
                  :width="240"
                  :native-scrollbar="false"
                  show-trigger
                >
                  <n-menu
                    :collapsed-width="64"
                    :collapsed-icon-size="22"
                    :options="menuOptions"
                  />
                </n-layout-sider>
                <n-layout-content content-style="padding: 24px; height: calc(100vh - 64px); overflow-y: auto;">
                  <router-view />
                </n-layout-content>
              </n-layout>
            </n-layout>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
</style>
