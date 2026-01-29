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
import heroBg from '../assets/banner/hero-bg.jpg';

// 2. Partner Logos
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';
import StanageLogo from '../assets/Stanage_logo/Stanage_Black.png';

// --- NAVIGATION LOGIC ---
const router = useRouter();

const goToMap = () => {
  router.push('/map'); 
};

const goToDocs = () => {
  router.push('/documentation'); 
};

const goToFram = () => {
  router.push('/fram'); 
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
            High-resolution measurements of glacier flow in Greenland and Antarctica using Sentinel-1 SAR imagery.
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
          Glaciers in Greenland and Antarctica can accelerate, thin and retreat in response to changes in air and ocean temperature. 
		  In the <RouterLink to="/fram" class="text-link"><strong>FRAM Project</strong></RouterLink>, 
		  we are using the Sentinel-1 satellites to monitor changes in glacier flow speed in near real-time.
		  <RouterLink to="/map" class="text-link"><strong>SHIVER</strong></RouterLink>
		  provides an interactive platform for visualizing and extracting our measurements of ice flow
		  across west Greenland and the Antarctica Peninsula. 
        </p>
        
        <div class="features-grid">
          <div class="feature-card" @click="goToFram">
            <h3>Flow Response of Antarctica to Meltwater (FRAM)</h3>
            <p>Combining satellite and field-based measurements to understand how Antarctic glaciers are responding to increasing meltwater supply.</p>
          </div>
          <div class="feature-card" @click="goToMap">
            <h3>Sheffield Ice Velocity ExploreR (SHIVER)</h3>
            <p>Instant visualisation and extraction of velocity timeseries. Utilizing cloud-based architecture for low-latency data access.</p>
          </div>
          <div class="feature-card" @click="goToDocs">
            <h3>Sentinel-1 Cross-correlation for Accurate Determination of Ice velocity (SCADI)</h3>
            <p>Learn how ice motion is measured ~weekly, regardless of weather and during polar darkness.</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="partners-footer">
      <div class="footer-content">
        
        <div class="partner-group">
          <h4>Lead Institutions</h4>
		   <a href="https://sheffield.ac.uk/" target="_blank" rel="noopener noreferrer">
			  <img :src="sheffieldLogo" alt="University of Sheffield" class="partner-logo" />
		   </a>
		   <br>
		   <a href="https://lamont.columbia.edu/" target="_blank" rel="noopener noreferrer">
			  <img :src="LDEOLogo" alt="LDEO" class="partner-logo" />
		   </a>
        </div>
        
        <div class="partner-group">
          <h4>Funded By</h4>
		  <a href="https://www.ukri.org/councils/nerc/" target="_blank" rel="noopener noreferrer">
			  <img :src="UKRILogo" alt="UKRI" class="partner-logo" />
		   </a>
		  <br>
		  <a href="https://www.nsf.gov/awardsearch/show-award/?AWD_ID=2053169" target="_blank" rel="noopener noreferrer">
			  <img :src="NSFLogo" alt="NSF" class="partner-logo" />
		   </a>
		  <br>
		  The FRAM project is funded by NSFGEO-NERC <br>
		  Grant Number: # 2053169, "Investigating the <br> 
		  Direct Influence of Meltwater on Antarctic Ice Sheet Dynamics
        </div>
		
		<div class="partner-group">
          <h4>Powered by</h4>
		  <a href="https://docs.hpc.shef.ac.uk/en/latest/stanage" target="_blank" rel="noopener noreferrer">
			  <img :src="StanageLogo" alt="Stanage" class="partner-logo" />
		   </a>
		  <br>
		  SCADI and SHIVER are powered by the University of Sheffield HPC Stanage <br>
        </div>
        
        <div class="partner-group">
          <h4>Contact</h4>
          <p>
		  SHIVER Project Team<br>
		  School of Geography and Planning, University of Sheffield, UK
		  <br><br>
		  FRAM Project Team<br>
		  Lamont-Doherty Earth Observatory, Columbia University, USA
		  </p>
        </div>
	  
	  <div class="partner-group">
          <h4>How to cite</h4>
          <p>
		  The recommended citation for this data is 
		  "Ice velocity generated using SCADI (Davison et al., 2020; Tuckett et al., 2019) and provided by the FRAM/SHIVER project (Kingslake/Sole)."
		  <br><br>
		  Davison, B.J., Sole, A.J., Cowton, T.R., Lea, J.M., Slater, D.A., Fahrner, D. and Nienow, P.W., 2020. Subglacial drainage evolution modulates seasonal ice flow variability of three tidewater glaciers in southwest Greenland. Journal of Geophysical Research: Earth Surface, 125(9), p.e2019JF005492. DOI: https://doi.org/10.1029/2019JF005492. 
		  <br><br>
		  Tuckett, P.A., Ely, J.C., Sole, A.J., Livingstone, S.J., Davison, B.J., Melchior van Wessem, J. and Howard, J., 2019. Rapid accelerations of Antarctic Peninsula outlet glaciers driven by surface melt. Nature Communications 10, 4311. https://doi.org/10.1038/s41467-019-12039-2.
		  <br><br>
		  Kingslake/Sole : Flow Response of Antarctic Ice to Meltwater/Sheffield Ice Velocity ExploreR
		  </p>
        </div>
	  
	  <div class="partner-group">
          <h4>Work with us</h4>
          <p>
		  Find us on github: ...to do...
		  <br>
		  or get in touch for custom velocity products.
		  </p>
        </div>
      </div>
      
      <div class="copyright">
        &copy; {{ new Date().getFullYear() }} SHIVER Project. All rights reserved.
      </div>
    </footer>

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