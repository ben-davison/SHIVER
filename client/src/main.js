import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'
import App from './App.vue'
import AppLink from './components/AppLink.vue'
import { routes, scrollBehavior } from './router/index.js'
import './style.css'

export const createApp = ViteSSG(
  // 1. The root component
  App,
  
  // 2. Vue-router options
  { 
    routes, 
    base: '/SHIVER/', 
    scrollBehavior 
  },
  
  // 3. Setup function (runs on both Client and Server builds)
  ({ app, router, isClient }) => {
    
    // Register Pinia
    const pinia = createPinia()
    app.use(pinia)

    // Register Global Components
    app.component('AppLink', AppLink)

    // GLOBAL GUARD
    router.beforeEach((to, from, next) => {
      // isClient ensures this ONLY runs in the user's browser.
      // If it runs on the build server, sessionStorage will throw a crash error.
      if (isClient) {
        // 1. Check specifically for the user token
        const isUserLoggedIn = sessionStorage.getItem('shiver_token');
        
        // 2. If the route requires auth, but the token is missing...
        if (to.meta.requiresAuth && !isUserLoggedIn) {
          next('/?login=required');
        } else {
          next();
        }
      } else {
        // If we are in the Node.js build process, just let the crawler pass
        next(); 
      }
    });
  }
)