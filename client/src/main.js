import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Import the router we just created

import './style.css' // Keep the default styles for now

const app = createApp(App)

app.use(router) // Tell the app to use the router

app.mount('#app')