import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import hljs from 'highlight.js/lib/core';
import json from 'highlight.js/lib/languages/json';

hljs.registerLanguage('json', json);
import { dragListDirective } from 'vue3-drag-directive'

const app = createApp(App)

app.config.globalProperties.hljs = hljs

app.use(createPinia())
app.use(router)
app.directive('drag', dragListDirective)

app.mount('#app')
