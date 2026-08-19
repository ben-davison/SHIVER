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
import DocWhatIsZarr from '../views/documentation/DocWhatIsZarr.vue'
import DocContributingData from '../views/documentation/DocContributingDataView.vue'
import DocUnifiedData from '../views/documentation/DocUnifiedData.vue'
import DocDataComparison from '../views/documentation/DocDataComparison.vue'
import DocTimeseriesExplorer from '../views/documentation/DocTimeseriesExplorerView.vue'
import DocNetcdfExtractor from '../views/documentation/DocNetcdfExtractorView.vue'
import DocCloudView from '../views/documentation/DocCloudView.vue'
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
      { path: 'whatiszarr', name: 'doc-whatiszarr', component: DocWhatIsZarr },
      { path: 'contributingdata', name: 'doc-contributingdata', component: DocContributingData },
      { path: 'unifieddata', name: 'doc-unifieddata', component: DocUnifiedData },
      { path: 'datacomparison', name: 'doc-datacomparison', component: DocDataComparison },
      { path: 'timeseriesexplore', name: 'doc-timeseriesexplore', component: DocTimeseriesExplorer },
      { path: 'netcdfextract', name: 'doc-netcdfextract', component: DocNetcdfExtractor },
	  { path: 'cloud', name: 'doc-cloud', component: DocCloudView },
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