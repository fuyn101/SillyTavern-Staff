import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { darkTheme, type GlobalTheme } from 'naive-ui';

export const useThemeStore = defineStore('theme', () => {
  // a null theme is a light theme
  const theme = ref<GlobalTheme | null>(darkTheme);

  const isDark = computed(() => theme.value === darkTheme);

  function toggleTheme() {
    theme.value = theme.value === darkTheme ? null : darkTheme;
  }

  return { theme, isDark, toggleTheme };
});
