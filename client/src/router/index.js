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

// Export the scroll behavior
export const scrollBehavior = (to, from, savedPosition) => {
  if (to.hash) {
    return { el: to.hash, behavior: 'smooth' }
  }
  return { top: 0 }
}

// Export the raw routes array
export const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/map', name: 'map', component: MapView },
  { path: '/cube', name: 'cube', component: CubeView, meta: { requiresAuth: true } },
  { 
    path: '/documentation', 
    component: DocumentationLayout,
    children: [
      { path: '', redirect: { name: 'doc-overview' } },
      { path: 'overview', name: 'doc-overview', component: DocOverviewView },
      { path: 'greenland', name: 'doc-greenland', component: DocGreenlandView },
      { path: 'antarctic', name: 'doc-antarctic', component: DocAntarcticView },
      { path: 'shift', name: 'doc-shift', component: DocShiftView },
      { path: 'datacubegen', name: 'doc-datacubegen', component: DocDataCubeGenView },
      { path: 'timeseriesexplore', name: 'doc-timeseriesexplore', component: DocTimeseriesExplorerView },
      { path: 'cubeextract', name: 'doc-cubeextract', component: DocCubeExtractorView },
      { path: 'citation', name: 'doc-citation', component: DocCitationView }
    ]
  },
  { 
    path: '/projects', 
    component: ProjectLayout,
    children: [
      { path: '', redirect: { name: 'proj-overview' } },
      { path: 'overview', name: 'proj-overview', component: ProjOverviewView }
    ]
  },
  { path: '/people', name: 'people', component: PeopleView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/profile', name: 'profile', component: ProfileView },
  { path: '/reset-password', name: 'reset-password', component: ResetPasswordView }
]