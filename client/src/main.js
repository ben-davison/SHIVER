import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import AppLink from './components/AppLink.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.component('AppLink', AppLink)

app.mount('#app')