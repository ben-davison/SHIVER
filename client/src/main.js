import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import "vanilla-cookieconsent/dist/cookieconsent.css";
import { initCookieConsent } from './utils/cookieConsent'; 

// 1. Define a global dummy 'gtag' function immediately.
// This prevents "gtag is not defined" errors if event() is called before consent.
window.dataLayer = window.dataLayer || [];
window.gtag = function() { window.dataLayer.push(arguments); };

const app = createApp(App)

app.use(router)

// 2. Initialize the Cookie Banner (Passing app & router so we can start GA later)
initCookieConsent(app, router);

app.mount('#app')