import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { dragListDirective } from 'vue3-drag-directive'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.directive('drag', dragListDirective)

app.mount('#app')
