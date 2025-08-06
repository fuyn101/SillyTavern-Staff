<script setup lang="ts">
import Breadcrumb from "@/components/Breadcrumb.vue";
import { darkTheme } from "naive-ui";
</script>

<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <n-loading-bar-provider>
            <div class="app">
              <Breadcrumb />
              <router-view />
            </div>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.app {
  height: 100vh;
  width: 100vw;
}
</style>
