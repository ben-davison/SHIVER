import { createApp } from 'vue'
import App from './App.vue'
import AppLink from './components/AppLink.vue'
import router from './router'
import './style.css'

const app = createApp(App)

app.use(router)

app.component('AppLink', AppLink)
app.mount('#app')