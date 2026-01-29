import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MapView.vue'
import DocumentationView from '../views/DocumentationView.vue'
import FramView from '../views/FramView.vue'
import PeopleView from '../views/PeopleView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  // Jump back to top of page when changing pages
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
  
  // Define routes
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/map', name: 'map', component: MapView },
    { path: '/documentation', name: 'documentation', component: DocumentationView },
    { path: '/fram', name: 'fram', component: FramView },
    { path: '/people', name: 'people', component: PeopleView }
  ]
})

export default router