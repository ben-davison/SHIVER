<script setup>
/**
 * FRAM PROJECT VIEW
 * A dedicated page for the FRAM Project details.
 */

// --- IMPORT FOOTER LOGOS (Consistency) ---
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';

// Content photos
import fieldworkImg1 from '../assets/images/fieldwork_photo1.jpg';
import velocityImg1 from '../assets/images/velocity_photo1.png';
import deploymentImg from '../assets/images/deployments.png';

</script>

<template>
  <div class="page-container">
    
    <main class="content-wrapper">
      <div class="text-container">
        <h1>The FRAM Project</h1>
        <p class="subtitle">Flow Response of Antarctica to Meltwater</p> <hr class="divider" />

        <section class="project-details">
          <h2>About the Project</h2>
          <p>
            This project is jointly funded by the UK Natural Environment Research Council (NERC) and the US National Science Foundation (NSF). 
			NSF hosts a page about the project
			<a href="https://www.nsf.gov/awardsearch/show-award/?AWD_ID=2053169" target="_blank" rel="noopener" class="text-link">
			here</a>.
			It is inspired by a paper published by the UK members of the team, 
			(<a href="https://www.nature.com/articles/s41467-019-12039-2" target="_blank" rel="noopener" class="text-link">Tuckett et al., 2019</a>).
          </p>
          
          <div class="highlight-box">
            <h3>Project Hypotheses</h3>
            <ul>
              <li>H1: Short-term changes in grounded ice velocity on the Antarctic Peninsula are due to meltwater injection to the bed.</li>
              <li>H2: Meltwater injection to the bed results in widespread short-term velocity fluctuations around Antarctica today.</li>
              <li>H3: Meltwater injection to the bed results in a measurable increase in mean annual ice discharge.</li>
            </ul>
          </div>
		  
		  <br>
		  The project is combining fieldwork and remote sensing to determine whether meltwater directly affects the velocity 
		  of Antarctic Peninsula outlet glaciers, how widespread it is and how important it is on annual timescales.
		  
		  <div class="highlight-box">
            <h3>Fieldwork</h3>
            <p>
			  With support from the full project team, a small group of three researchers went to Flask Glacier on the Antarctic Peninsula in 
			  November/December 2024 and another group went again in 2025. The teams deployed a suite of instruments on the glacier surface
			  to measure ice motion and meltwater across a range of timescales and resolutions.
			  </p>
			  <img :src="deploymentImg" alt="Flask Glacier deployment map" class="box-image" />
			  <ul>
              <li>Global Navigation Satellite System (GNSS) instruments to measure horizontal and vertical ice motion.</li>
              <li>Automatic weather station (AWS) measurements of surface melt and related variables</li>
              <li>Uncrewed Aerial Vehicle (UAV) photographs and measurements of ice surface elevation</li>
			  <li>Ice-penetrating radar measurements of ice thickness and ice motion (ApRES)</li>
			  <li>Passive seismic detection of subglacial water flow</li>
            </ul>
			<br>
			<img :src="fieldworkImg1" alt="Wingtra UAV flying on Flask Glacier" class="box-image" />
          </div>
		  
		  <div class="highlight-box">
            <h3>Remote sensing</h3>
            <p>
			  In this project, we are using satellite images to measure ice motion by tracking the movement of surface features
			  (like crevasses) as they are advected with ice flow. We use state-of-the-art 
			  <RouterLink to="/documentation" class="text-link">image processing techniques</RouterLink>
			  to achieve
			  this. 
			  <br><br>
			  The primary satellite system we use is the European Space Agency's 
			  Sentinel-1 satellite constellation, because it can see the glacier surface even during the long polar night and through clouds,
              allowing us to develop an almost unbroken record of ice motion across the Antarctic Peninsula every 6-12 days at 200 x 200 m 
			  resolution from October 2014-present. We supplement the Sentinel-1 observations with images from Sentinel-2 and the Landsat
			  archive, which require clear skies and sunlight.
			  <br>
			  <img :src="velocityImg1" alt="Example Sentinel-1 velocity field" class="box-image" />
            </p>
          </div>
		  
		  
        </section>
      </div>
    </main>

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
          <h4>Contact</h4>
          <p>
		  SHIVER Project Team<br>
		  School of Geography and Planning, University of Sheffield, UK
		  <br><br>
		  FRAM Project Team<br>
		  Lamont-Doherty Earth Observatory, Columbia University, USA
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
/* --- LAYOUT --- */
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fcfcfc;
}

.content-wrapper {
  flex: 1; /* Pushes footer to bottom */
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.text-container {
  max-width: 800px;
  width: 100%;
}

/* --- TYPOGRAPHY --- */
h1 {
  font-size: 3rem;
  color: #0b1e3b;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.5rem;
  color: #5a9bd4;
  font-weight: 300;
  margin-top: 0;
}

.divider {
  border: 0;
  height: 1px;
  background: #ddd;
  margin: 40px 0;
}

h2 {
  color: #0b1e3b;
  margin-top: 0;
}

p, li {
  line-height: 1.8;
  color: #444;
  font-size: 1.1rem;
}

/* --- HIGHLIGHT BOX --- */
.highlight-box {
  background-color: #eef7ff;
  border-left: 5px solid #0056b3;
  padding: 30px;
  margin-top: 40px;
  border-radius: 4px;
}

.highlight-box h3 {
  margin-top: 0;
  color: #0056b3;
}

.highlight-box ul {
  margin-bottom: 0;
  padding-left: 20px;
}

.box-image {
  display: block;
  max-width: 100%;       /* Ensures image never exceeds box width */
  height: auto;          /* Maintains aspect ratio */
  margin: 15px 0;        /* Adds space above and below the image */
  border-radius: 4px;    /* Optional: slightly rounded corners */
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Optional: subtle shadow */
}

/* --- FOOTER STYLES (Standardized) --- */
.partners-footer {
  background-color: #0b1e3b;
  color: white;
  padding: 50px 20px 20px;
  margin-top: auto;
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

.partner-logo {
  height: 60px;
  width: auto;
  display: block;
  max-width: 100%;
  background-color: white;
  padding: 8px;
  border-radius: 6px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.copyright {
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 20px;
  font-size: 0.8rem;
  color: #888;
}
</style>