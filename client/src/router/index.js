import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MapView.vue'
import DocumentationView from '../views/DocumentationView.vue'
import FramView from '../views/FramView.vue'
import PeopleView from '../views/PeopleView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  // Jump back to top of page when changing pages
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
  
  // Define routes { path: '/cube', name: 'cube', component: CubeView, meta: { requiresAuth: true } },
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/map', name: 'map', component: MapView },
    { path: '/documentation', name: 'documentation', component: DocumentationView },
    { path: '/fram', name: 'fram', component: FramView },
    { path: '/people', name: 'people', component: PeopleView },
	{ path: '/login', name: 'login', component: LoginView },
	{ path: '/profile', name: 'profile', component: ProfileView },
	{ path: '/reset-password', name: 'reset-password', component: ResetPasswordView }
  ]
})

// GLOBAL GUARD
router.beforeEach((to, from, next) => {
  // 1. Check specifically for the user token
  const isUserLoggedIn = sessionStorage.getItem('shiver_token');
  
  // 2. If the route requires auth, but the token is missing...
  if (to.meta.requiresAuth && !isUserLoggedIn) {
    // open login modal
    next('/?login=required');
  } else {
    // 3. Otherwise, let them pass
    next();
  }
});

export default router