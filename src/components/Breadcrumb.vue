<template>
  <n-breadcrumb>
    <n-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
      <router-link v-if="index < breadcrumbs.length - 1" :to="item.path">
        {{ item.meta.breadcrumb }}
      </router-link>
      <span v-else>{{ item.meta.breadcrumb }}</span>
    </n-breadcrumb-item>
  </n-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.breadcrumb)
  return matched
})
</script>
