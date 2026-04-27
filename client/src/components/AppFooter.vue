<script setup>
// --- IMPORT LOGOS FOR FOOTER ---
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';
import StanageLogo from '../assets/Stanage_logo/Stanage_Black.png';
</script>

<template>
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
        <p class="footer-text">
          The FRAM project is funded by NSFGEO-NERC <br>
          Grant Number: #2053169, "Investigating the <br> 
          Direct Influence of Meltwater on Antarctic Ice Sheet Dynamics"
        </p>
      </div>
        
      <div class="partner-group">
        <h4>Powered by</h4>
        <a href="https://docs.hpc.shef.ac.uk/en/latest/stanage" target="_blank" rel="noopener noreferrer">
          <img :src="StanageLogo" alt="Stanage" class="partner-logo" />
        </a>
        <br>
        <p class="footer-text">SHIFT and SHIVER are powered by the University of Sheffield HPC Stanage</p>
      </div>
        
      <div class="partner-group">
        <h4>Contact</h4>
        <p class="footer-text">
          SHIVER Project Team<br>
          School of Geography and Planning, University of Sheffield, UK <br>
          Email: shiver@sheffield.ac.uk
          <br><br>
          FRAM Project Team<br>
          Lamont-Doherty Earth Observatory, Columbia University, USA
        </p>
      </div>
	
	  <div class="partner-group">
		  <h4>Work with us</h4>
		  <p>
			Find us on github: https://github.com/ben-davison/SHIVER
		  <br>
			Get in touch for custom velocity products or if you find any bugs: shiver@sheffield.ac.uk
		  </p>
		</div>
		
		<div class="partner-group">
		  <h4><AppLink to="/documentation/citation" class="text-link">How to cite</AppLink></h4>
		</div>
    </div>
    
    <div class="copyright">
      &copy; {{ new Date().getFullYear() }} SHIVER Project. Licensed under GNU GPL-3.0.
    </div>
  </footer>
</template>

<style scoped>
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
  text-align: center;
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

.footer-text {
  font-size: 0.85rem;
  line-height: 1.4;
  color: #ccc;
  margin: 0;
}

.copyright {
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 20px;
  font-size: 0.8rem;
  color: #888;
}
</style>