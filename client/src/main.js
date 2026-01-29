import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initCookieConsent } from './utils/cookieConsent';
import * as VueGtagModule from "vue-gtag";
const VueGtag = VueGtagModule.default || VueGtagModule;
import './style.css'


const app = createApp(App)

app.use(router)

app.use(VueGtag, {
  config: { id: "G-4YGWRB6RCZ" },
  bootstrap: false
}, router);

// Initialize banner (no args needed now)
initCookieConsent();

app.mount('#app')