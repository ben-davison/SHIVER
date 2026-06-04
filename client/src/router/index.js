import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MultiSourceMap.vue'
import CubeView from '../views/MultiSourceCube.vue'
import PeopleView from '../views/PeopleView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'

// Documentation pages
import DocumentationLayout from '../views/documentation/DocumentationLayout.vue'
import DocOverviewView from '../views/documentation/DocOverviewView.vue'
import DocGreenlandView from '../views/documentation/DocGreenlandView.vue'
import DocAntarcticView from '../views/documentation/DocAntarcticView.vue'
import DocShiftView from '../views/documentation/DocShiftView.vue'
import DocDataCubeGenView from '../views/documentation/DocDataCubeGenView.vue'
import DocTimeseriesExplorerView from '../views/documentation/DocTimeseriesExplorerView.vue'
import DocCubeExtractorView from '../views/documentation/DocCubeExtractorView.vue'
import DocCitationView from '../views/documentation/DocCitationView.vue'

// Project pages
import ProjectLayout from '../views/projects/ProjLayout.vue'
import ProjOverviewView from '../views/projects/ProjOverviewView.vue'

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
	{ path: '/cube', name: 'cube', component: CubeView, meta: { requiresAuth: true } },
    { 
      path: '/documentation', 
      component: DocumentationLayout, // Parent layout component
      children: [
        { path: '', redirect: { name: 'doc-overview' } }, // Redirect base to overview
        { path: 'overview', name: 'doc-overview', component: DocOverviewView },
        { path: 'greenland', name: 'doc-greenland', component: DocGreenlandView },
        { path: 'antarctic', name: 'doc-antarctic', component: DocAntarcticView },
        { path: 'shift', name: 'doc-shift', component: DocShiftView }, // Your old 1-7 sections
        { path: 'datacubegen', name: 'doc-datacubegen', component: DocDataCubeGenView },
		{ path: 'timeseriesexplore', name: 'doc-timeseriesexplore', component: DocTimeseriesExplorerView },
		{ path: 'cubeextract', name: 'doc-cubeextract', component: DocCubeExtractorView },
        { path: 'citation', name: 'doc-citation', component: DocCitationView }
      ]
    },
	{ 
      path: '/projects', 
      component: ProjectLayout, // Parent layout component
      children: [
        { path: '', redirect: { name: 'proj-overview' } }, // Redirect base to overview
        { path: 'overview', name: 'proj-overview', component: ProjOverviewView }
      ]
    },
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