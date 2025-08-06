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
      path: '/editor-main',
      name: 'MainEditorView',
      component: () => import('@/views/MainEditorView.vue'),
      meta: { breadcrumb: 'Main Editor' }
    },
    {
      path: '/file-manager',
      name: 'FileManager',
      component: () => import('@/views/FileManagerView.vue'),
      meta: { breadcrumb: 'File Manager' }
    }
  ],
})

export default router
