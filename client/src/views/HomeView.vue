<script setup>
/**
 * HOME VIEW
 * The landing page for the application.
 * * Key Features:
 * 1. Hero Banner: Uses a dynamic background image imported from assets.
 * 2. Project Overview: Static text explaining the SHIVER project.
 * 3. Footer: Displays partner logos and funding agencies.
 */

import { useRouter } from 'vue-router';

// --- IMAGE ASSET IMPORTS ---
// Importing images here ensures Vue bundlers (Vite/Webpack) process them correctly.
// This prevents "missing image" errors when deploying the site.

// 1. Hero Background (Check this path matches your folder structure exactly)
import heroBg from '../assets/banner/hero-bg_v2.jpg';

// 2. Partner Logos
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';
import StanageLogo from '../assets/Stanage_logo/Stanage_Black.png';
import DocSectionCard from '../components/DocSectionCard.vue' 
import DocSectionCardShort from '../components/DocSectionCardShort.vue' 
import { useHead } from '@unhead/vue'

// -----------------------------------------------------------------------------------------
// --- SEO ---------------------------------------------------------------------------------
useHead({
  title: 'SHIVER | Home Page',
  meta: [
    { 
      name: 'description', 
      content: 'Explore the flow response of Greenland and Antarctica to climate change. Glacier flow transports ice into the ocean, contributing to global sea level rise. Increases in air and ocean temperature can lead to acceleration of ice flow and faster sea level rise. Therefore, measurements of ice flow are crucial for understanding the response of Greenland and Antarctica to climate change and for monitoring their contribution to sea level rise. In response to this need, researchers have used the abundance of satellite imagery to measure ice sheet flow. SHIVER provides an interactive platform for exploring, visualizing and extracting these measurements, with the aim of accelerating scientific discovery and educating interested parties.' 
    }
  ]
})

// --- NAVIGATION LOGIC ---
const router = useRouter();

const goToMap = () => {
  router.push('/map'); 
};


</script>

<template>
  <div class="home-container">
    
    <section class="hero-banner" :style="{ backgroundImage: `url(${heroBg})` }">
      
      <div class="hero-overlay">
        <div class="hero-content">
          <h1 class="main-title">SHIVER</h1>
          <p class="subtitle">SHeffield Ice Velocity ExploreR</p>
          <p class="tagline">
            Explore the flow response of Greenland and Antarctica to climate change.
          </p>
          
          <div class="action-buttons">
            <button class="btn-primary" @click="goToMap">Explore Data</button>
          </div>
        </div>
      </div>
    </section>

    <section class="project-overview">
      <div class="content-wrapper">
        <h2>Monitoring Ice Flow in a Warming World</h2>
        <p>
          Glacier flow transports ice into the ocean, contributing to global sea level rise. 
		  Increases in air and ocean temperature can lead to acceleration of ice flow and faster sea level rise. 
		  Therefore, measurements of ice flow are crucial for understanding the response of 
		  Greenland and Antarctica to climate change and for monitoring their contribution to sea level rise.
		</p>
		<p>
		  In response to this need, researchers have used the abundance of satellite imagery to measure ice sheet
		  flow. <RouterLink to="/map" class="text-link"><strong>SHIVER</strong></RouterLink>
		  provides an interactive platform for exploring, visualizing and extracting these measurements, with the aim
          of accelerating scientific discovery and educating interested parties.
        </p>
		
		<DocSectionCardShort 
			title="Sheffield Ice Velocity ExploreR (SHIVER) - Timeseries Explorer" 
			to="/map"
		  >
			<template #image>
			  <img src="../assets/documentation/overview/timeseries_thumb.png" alt="Timeseries graph">
			</template>
			<template #description>
			  <p>
			    The SHIVER Timeseries Explorer utilizes cloud-based architecture to provide instant visualisation and extraction of ice sheet velocity measurements for Greenland and Antarctica in one simple interface.
			  </p>
			</template>
		</DocSectionCardShort>
		
		<DocSectionCardShort 
			title="Sheffield Ice Velocity ExploreR (SHIVER) - Data Cube Extractor" 
			to="/cube"
		  >
			<template #image>
			  <img src="../assets/images/NetCDF.png" alt="NetCDF schematic">
			</template>
			<template #description>
			  <p>
			    The SHIVER Data Cube Extractor allows rapid generation and download of ice velocity data cubes for any time period and region in Greenland and Antarctica in one simple interface.
			  </p>
			</template>
		</DocSectionCardShort>
		
		<DocSectionCardShort 
			title="SHeffield Ice Flow Tracker (SHIFT)" 
			to="/documentation/shift"
		  >
			<template #image>
			  <img src="../assets/documentation/CC.jpg" alt="SHIFT Diagram">
			</template>
			<template #description>
			  <p>
			    SHIFT is our processing system to generate the some of the ice velocity measurements available in SHIVER.
			    With it, we measure ice motion ~weekly, regardless of weather and during polar darkness.
			  </p>
			</template>
		</DocSectionCardShort>
		
	   </div>
    </section>

  </div>
</template>

<style scoped>
/* --- 1. MAIN LAYOUT CONTAINER --- */
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* Ensures footer sits at bottom even on empty pages */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* --- 2. HERO SECTION STYLES --- */
.hero-banner {
  /* Note: background-image is handled in the HTML template via inline style */
  background-size: cover;
  background-position: center;
  height: 85vh; /* Takes up 85% of the viewport height */
  position: relative;
  background-color: #0b1e3b; /* Fallback color if image loads slowly */
}

.hero-overlay {
  /* A gradient overlay to darken the image for better text contrast */
  background: linear-gradient(to bottom, rgba(0, 20, 50, 0.7), rgba(0, 20, 50, 0.4));
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.hero-content {
  color: white;
  max-width: 800px;
  padding: 20px;
}

.main-title {
  font-size: 5rem; 
  font-weight: 800;
  margin: 0;
  letter-spacing: 4px;
  text-shadow: 0 4px 10px rgba(0,0,0,0.5);
}

.subtitle {
  font-size: 1.5rem;
  font-weight: 300;
  margin-top: 5px;
  color: #aab8c2;
  letter-spacing: 2px;
}

.tagline {
  font-size: 1.2rem;
  margin: 30px auto;
  line-height: 1.6;
  max-width: 600px;
  color: #e1e8ed;
}

/* --- 3. BUTTON STYLES --- */
.action-buttons {
  margin-top: 40px;
  display: flex;
  gap: 20px;
  justify-content: center;
}

.btn-primary {
  padding: 15px 40px;
  font-size: 1.1rem;
  font-weight: bold;
  background-color: #0056b3;
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
  box-shadow: 0 4px 15px rgba(0, 86, 179, 0.4);
}

.btn-primary:hover {
  background-color: #004494;
  transform: translateY(-2px); /* Slight lift effect */
}

.btn-secondary {
  padding: 15px 40px;
  font-size: 1.1rem;
  font-weight: bold;
  background-color: transparent;
  color: white;
  border: 2px solid white;
  border-radius: 50px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.btn-secondary:hover {
  background-color: white;
  color: #0b1e3b;
}

/* --- 4. PROJECT OVERVIEW STYLES --- */
.project-overview {
  padding: 80px 20px;
  background-color: #f8f9fa;
  color: #333;
  text-align: center;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
}

.project-overview h2 {
  font-size: 2.5rem;
  color: #0056b3;
  margin-bottom: 20px;
}

.project-overview p {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #555;
  margin-bottom: 50px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.05);
  transition: transform 0.3s;
  cursor: pointer;
}

.feature-card:hover {
  border-color: #0056b3; /* Blue border on hover */
  transform: translateY(-8px); /* Lifts up slightly more than others */
  background-color: #f0f8ff; /* Very pale blue background */
}

.feature-card h3 {
  color: #0b1e3b;
  margin-top: 0;
}

/* --- 5. FOOTER STYLES --- */
.partners-footer {
  background-color: #0b1e3b; /* Dark Navy to match Header/Hero */
  color: white;
  padding: 50px 20px 20px;
  margin-top: auto; /* Pushes footer to bottom of flex container */
}

.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  gap: 40px;
  margin-bottom: 40px;
}

.partner-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.partner-group h4 {
  text-transform: uppercase;
  font-size: 0.9rem;
  color: #5a9bd4;
  margin-bottom: 15px;
  letter-spacing: 1px;
}

/* Standardized Logo Size */
.partner-logo {
  height: 60px;       /* Fixed height ensures uniformity */
  width: auto;        /* Auto width prevents distortion */
  display: block;
  max-width: 100%;
  
  /* Styling to make logos pop against the dark background */
  background-color: white; 
  padding: 8px;
  border-radius: 6px;
  
  /* Interactive hover effect */
  opacity: 0.9;
  transition: opacity 0.3s;
}

.partner-logo:hover {
  opacity: 1.0;
}

.copyright {
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 20px;
  font-size: 0.8rem;
  color: #888;
}
</style>