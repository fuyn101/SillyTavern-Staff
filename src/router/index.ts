import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'HomeView',
      component: () => import('@/views/HomeView.vue'),
      meta: { breadcrumb: 'Home' }
    },
    {
      path: '/editor',
      name: 'EditorView',
      component: () => import('@/views/CharacterEditorView.vue'),
      meta: { breadcrumb: 'Editor' },

    },
    {
      path: '/preset-editor',
      name: 'PresetEditorView',
      component: () => import('@/views/PresetEditorView.vue'),
      meta: { breadcrumb: 'Preset Editor' }
    },
    {
      path: '/file-manager',
      name: 'FileManager',
      component: () => import('@/views/FileManagerView.vue'),
      meta: { breadcrumb: 'File Manager' }
    },
    {
      path: '/two-page-editor',
      name: 'TwoPageEditor',
      component: () => import('@/views/PresetEditorView.vue'),
      meta: { breadcrumb: '预设对比编辑器' }
    }
  ],
})

export default router
