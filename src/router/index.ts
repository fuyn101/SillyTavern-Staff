import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'HomeView',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/editor',
      name: 'EditorView',
      component: () => import('@/views/CharacterEditorView.vue')
    },
    {
      path: '/two-page-editor',
      name: 'TwoPageEditorView',
      component: () => import('@/views/TwoPageEditorView.vue')
    }
  ],
})

export default router
