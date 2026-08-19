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
              <RouterLink to="/documentation/whatiszarr" active-class="active-doc-link">2. What is Zarr</RouterLink>
			  <ul class="sub-nav-list" v-show="$route.path === '/documentation/whatiszarr'">
				<li><a href="#" @click.prevent="handleHashNav('/documentation/whatiszarr', 'working-with-zarr')">Working with Zarr</a></li>
			  </ul>
            </li>
			
            <li>
              <RouterLink to="/documentation/contributingdata" active-class="active-doc-link">3. Contributing Datasets</RouterLink>
			    <ul class="sub-nav-list" v-show="$route.path === '/documentation/contributingdata'">
					<li><a href="#" @click.prevent="handleHashNav('/documentation/contributingdata', 'greenland-data')">Greenland</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/contributingdata', 'antarctica-data')">Antarctica</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/contributingdata', 'summary')">Summary</a></li>
              </ul>
            </li>
			
			<li>
              <RouterLink to="/documentation/unifieddata" active-class="active-doc-link">4. Unified Datasets</RouterLink>
			    <ul class="sub-nav-list" v-show="$route.path === '/documentation/unifieddata'">
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'overview')">Overview</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'zarr-chunk-definition')">Zarr Chunk Definition</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'ome-zarr')">OME-Zarr</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'reprojection')">Reprojection</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'timestamps')">Timestamps</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'measurement-error')">Error</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/unifieddata', 'variables')">Variables</a></li>
              </ul>
            </li>
            
            <li>
              <RouterLink to="/documentation/datacomparison" active-class="active-doc-link">5. Comparison of Datasets</RouterLink>
            </li>

			<li>
              <RouterLink to="/documentation/timeseriesexplore" active-class="active-doc-link">6. SHIVER Timeseries Explorer</RouterLink>
				<ul class="sub-nav-list" v-show="$route.path === '/documentation/timeseriesexplore'">
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'basic-usage')">Basic Usage</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'uploading-files-uploadicon')">Uploading Files</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'advanced-options-advancedicon')">Advanced Options</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'navigating-interpreting-the-map')">Navigating & Interpreting the Map</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'interpreting-the-chart')">Interpreting the Chart</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'output')">Output</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/timeseriesexplore', 'references')">References</a></li>
              </ul>
            </li>
			
			<li>
              <RouterLink to="/documentation/netcdfextract" active-class="active-doc-link">7. SHIVER Data Cube Extractor</RouterLink>
				<ul class="sub-nav-list" v-show="$route.path === '/documentation/netcdfextract'">
					<li><a href="#" @click.prevent="handleHashNav('/documentation/netcdfextract', 'basic-usage')">Basic Usage</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/netcdfextract', 'uploading-files-uploadicon')">Uploading Files</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/netcdfextract', 'navigating-interpreting-the-map')">Navigating & Interpreting the Map</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/netcdfextract', 'output')">Output</a></li>
					<li><a href="#" @click.prevent="handleHashNav('/documentation/netcdfextract', 'references')">References</a></li>
              </ul>
            </li>
			
			<li>
              <RouterLink to="/documentation/cloud" active-class="active-doc-link">8. Cloud Data Access</RouterLink>
            </li>
            
            <li>
              <RouterLink to="/documentation/citation" active-class="active-doc-link">9. Citation & License</RouterLink>
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