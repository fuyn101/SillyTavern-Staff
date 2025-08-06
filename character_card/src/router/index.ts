import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/editor'
    },
    {
      path: '/editor',
      name: 'EditorView',
      component: () => import('@/views/CharacterEditorView.vue')
    }
  ],
})

export default router
