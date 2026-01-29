import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 
import VueGtag from "vue-gtag";

import './style.css' // Keep the default styles for now
import "vanilla-cookieconsent/dist/cookieconsent.css";

const app = createApp(App)

app.use(router) // Tell the app to use the router

// Initialize Google Analytics
app.use(VueGtag, {
  config: { id: "G-4YGWRB6RCZ" } ,
  bootstrap: false
}, router); 

app.mount('#app')