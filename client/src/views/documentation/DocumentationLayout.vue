<script setup>
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// Smart navigation function for the sidebar
const handleHashNav = async (targetPath, sectionId) => {
  if (route.path !== targetPath) {
    // 1. If we are on a different page, tell the router to go to the new page + hash
    await router.push({ path: targetPath, hash: `#${sectionId}` });
  } else {
    // 2. If we are already on the correct page, just smooth scroll to the section
    const element = document.getElementById(sectionId);
    if (element) {
      const headerOffset = 100; // Accounts for your sticky header
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.scrollY - headerOffset;
      
      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth"
      });
      
      // Update the URL hash visually without triggering a jump
      history.replaceState(null, null, `#${sectionId}`);
    }
  }
};
</script>

<template>
  <div class="doc-page">
    <div class="doc-container">
      
      <aside class="doc-sidebar">
        <nav>
          <h3>Contents</h3>
          <ul class="main-nav-list">
            
            <li>
              <RouterLink to="/documentation/overview" active-class="active-doc-link">1. Documentation Overview</RouterLink>
            </li>
            
            <li>
              <RouterLink to="/documentation/greenland" active-class="active-doc-link">2. Greenland Data Sources</RouterLink>
			    <ul class="sub-nav-list" v-show="$route.path === '/documentation/greenland'">
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'introduction')">1. Introduction</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'shift')">2. SHIFT</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'promice')">3. PROMICE</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'measures_monthly')">4. MEaSUREs monthly</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'measures_quarterly')">5. MEaSUREs quarterly</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'measures_winter')">6. MEaSUREs winter</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'measures_annual')">7. MEaSUREs annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'itslive_annual')">8. ITS_LIVE Annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'mouginot_annual')">9. Mouginot Annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'enveo_annual')">10. ENVEO Annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_winter')">11. ESA CCI Winter</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_ers1_1991')">12. ESA CCI ERS-1</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_ers2_1995')">13. ESA CCI ERS-2</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_palsar')">14. ESA CCI PALSAR</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_ers_env')">15. ESA CCI ERS & Envisat</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_csk')">16. ESA CCI CSK</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_sentinel2')">17. ESA CCI Sentinel-2</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/greenland', 'esa_sentinel1')">18. ESA CCI Sentinel-1</a></li>
              </ul>
            </li>
            
            <li>
              <RouterLink to="/documentation/antarctic" active-class="active-doc-link">3. Antarctic Data Sources</RouterLink>
			    <ul class="sub-nav-list" v-show="$route.path === '/documentation/antarctic'">
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'introduction')">1. Introduction</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'shift')">2. SHIFT</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_monthly')">3. ENVEO Monthly</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_pig')">4. ENVEO (Pine Island)</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_ers')">5. ENVEO ERS</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_tsx')">6. ENVEO TSX</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_alos')">7. ENVEO ALOS</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_tsx_s1')">8. ENVEO TSX & Sentinel-1</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'enveo_tsx_palsar')">9. ENVEO TSX & PALSAR</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'measures_multiyear')">10. MEaSUREs multi-year</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'measures_annual')">11. MEaSUREs annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'measures_ase')">12. MEaSUREs ASE</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'itslive_annual')">13. ITS_LIVE annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'esa_annual')">14. ESA CCI annual</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'esa_sentinel1')">15. ESA CCI Sentinel-1</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'joughin_s1')">16. Joughin Sentinel-1</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'joughin_tsx')">17. Joughin TSX</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/antarctic', 'li_totten')">18. Li et al. (Totten)</a></li>
              </ul>
			  
            </li>
            
            <li>
              <RouterLink to="/documentation/shift" active-class="active-doc-link">4. SHIFT Algorithms</RouterLink>
              
              <ul class="sub-nav-list" v-show="$route.path === '/documentation/shift'">
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'introduction')">Introduction</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'overview')">1. Overview</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'data-sources')">2. Data Sources</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'pre-processing')">3. Pre-processing</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'algorithms')">4. Algorithms</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'post-processing')">5. Post-processing</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'mosaics')">6. Mosaics</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'automation')">7. Automation</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/shift', 'references')">7. References</a></li>
              </ul>
            </li>

            <li>
              <RouterLink to="/documentation/datacubegen" active-class="active-doc-link">5. Data Cube Generation</RouterLink>
            </li>
			
			<li>
              <RouterLink to="/documentation/timeseriesexplore" active-class="active-doc-link">6. SHIVER Timeseries Explorer</RouterLink>
              <ul class="sub-nav-list" v-show="$route.path === '/documentation/timeseriesexplore'">
                <li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'basic-usage')">1. Basic Usage</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'file-upload')">2. Uploading Files</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'advanced-options')">3. Advanced Options</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'map-interpret')">4. Interpreting the Map</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'chart-interpret')">5. Interpreting the Chart</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'output')">6. Output</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'references')">7. References</a></li>
              </ul>
            </li>
			
			<li>
              <RouterLink to="/documentation/cubeextract" active-class="active-doc-link">7. SHIVER Data Cube Extractor</RouterLink>
              <ul class="sub-nav-list" v-show="$route.path === '/documentation/cubeextract'">
                <li><a href="#" @click.prevent="handleHashNav('/documentation/cubeextract', 'basic-usage')">1. Basic Usage</a></li>
                <li><a href="#" @click.prevent="handleHashNav('/documentation/cubeextract', 'file-upload')">2. Uploading Files</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/cubeextract', 'map-interpret')">3. Interpreting the Map</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/cubeextract', 'output')">4. Output</a></li>
				<li><a href="#" @click.prevent="handleHashNav('/documentation/cubeextract', 'references')">5. References</a></li>
              </ul>
            </li>
            
            <li>
              <RouterLink to="/documentation/citation" active-class="active-doc-link">8. Citation & License</RouterLink>
            </li>
            
          </ul>
        </nav>
      </aside>

      <main class="doc-content">
        <router-view></router-view> 
      </main>

    </div>
  </div>
</template>

<style scoped>
/* --- LAYOUT --- */
.doc-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fcfcfc;
}

.doc-container {
  display: flex;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 20px;
  gap: 60px;
  flex: 1;
}

/* --- MASTER SIDEBAR --- */
.doc-sidebar {
  width: 250px;
  flex-shrink: 0;
  position: sticky;
  top: 40px; 
  height: fit-content;
  border-right: 2px solid #eee;
  padding-right: 20px;
}

.doc-sidebar h3 {
  margin-top: 0;
  color: #0b1e3b;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Main links */
.main-nav-list > li {
  margin-bottom: 12px;
}

.main-nav-list a {
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: all 0.2s;
  display: block;
  padding: 5px 0;
}

.main-nav-list a:hover {
  color: #0056b3;
}

.active-doc-link {
  color: #0056b3 !important;
  font-weight: 700 !important;
}

/* Sub-links (The expanded nested menu) */
.sub-nav-list {
  margin-top: 5px;
  margin-bottom: 15px;
  border-left: 2px solid #e1e8ed; /* Creates a nice vertical line showing hierarchy */
  margin-left: 10px;
  padding-left: 15px;
}

.sub-nav-list li {
  margin-bottom: 8px;
}

.sub-nav-list a {
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
  padding: 2px 0;
}

.sub-nav-list a:hover {
  color: #0056b3;
  transform: translateX(3px); /* Subtle indentation on hover */
}

/* Highlight the active sub-link based on URL hash (optional advanced styling) */
.sub-nav-list a:active,
.sub-nav-list a:focus {
  color: #0056b3;
  font-weight: 600;
}

/* --- MAIN CONTENT CONTAINER --- */
.doc-content {
  flex-grow: 1;
  max-width: 800px;
}

@media (max-width: 768px) {
  .doc-container {
    flex-direction: column;
  }
  .doc-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 2px solid #eee;
    padding-bottom: 20px;
    margin-bottom: 20px;
    position: static;
  }
}
</style>


/* --- SHARED DOCUMENTATION TYPOGRAPHY --- */
<style>
/* Target elements specifically inside the main content area */
.doc-content section {
  margin-bottom: 60px;
  scroll-margin-top: 100px; /* Ensures headers don't hide behind the navbar */
}

.doc-content h1 {
  font-size: 2.5rem;
  color: #0b1e3b;
  margin-bottom: 20px;
}

.doc-content h2 {
  font-size: 1.8rem;
  color: #0b1e3b;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
  margin-top: 0;
}

.doc-content h3 {
  font-size: 1.3rem;
  color: #444;
  margin-top: 25px;
}

.doc-content p, 
.doc-content li {
  line-height: 1.7;
  color: #444;
  font-size: 1.05rem;
}

.doc-content .intro-text {
  font-size: 1.2rem;
  color: #555;
  border-left: 4px solid #0056b3;
  padding-left: 20px;
}

/* Citation style */
.doc-content .citation-block {
  background: #f5f5f5;
  padding: 20px;
  font-family: 'Courier New', Courier, monospace;
  border-radius: 6px;
  border: 1px solid #ddd;
}


</style>