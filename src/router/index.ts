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
      component: () => import('@/features/character-editor/views/CharacterEditorView.vue'),
      meta: { breadcrumb: 'Editor' },
      redirect: '/editor/basic',
      children: [
        {
          path: 'basic',
          name: 'CharacterBasicEditor',
          component: () => import('@/features/character-editor/components/CharacterBasicEditor.vue'),
          meta: { breadcrumb: 'Basic Editor' }
        },
        {
          path: 'data',
          name: 'CharacterDataEditor',
          component: () => import('@/features/character-editor/components/CharacterDataEditor.vue'),
          meta: { breadcrumb: 'Data Editor' }
        }
      ]
    },
    {
      path: '/preset-editor',
      name: 'PresetEditorView',
      component: () => import('@/features/preset-editor/views/PresetEditorView.vue'),
      meta: { breadcrumb: 'Preset Editor' }
    },
    {
      path: '/file-manager',
      name: 'FileManager',
      component: () => import('@/features/file-manager/views/FileManagerView.vue'),
      meta: { breadcrumb: 'File Manager' }
    },
    {
      path: '/two-page-editor',
      name: 'TwoPageEditor',
      component: () => import('@/features/preset-editor/views/PresetEditorView.vue'),
      meta: { breadcrumb: '预设对比编辑器' }
    }
  ],
})

export default router
