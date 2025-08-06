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
      path: '/two-page-editor',
      name: 'TwoPageEditorView',
      component: () => import('@/views/TwoPageEditorView.vue'),
      meta: { breadcrumb: 'Two Page Editor' }
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
