<script setup>
// --- IMPORT LOGOS FOR FOOTER ---
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NERCLogo from '../assets/UKRI_logo/NERC_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';
import StanageLogo from '../assets/Stanage_logo/Stanage_Black.png';
</script>

<template>
  <footer class="partners-footer">
    <div class="footer-content">
      
      <div class="footer-column">
        <h4>Institutions & Partners</h4>
        <div class="logo-stack">
          <a href="https://sheffield.ac.uk/" target="_blank" rel="noopener noreferrer" class="logo-link">
            <img :src="sheffieldLogo" alt="University of Sheffield" class="partner-logo" />
          </a>
          <a href="https://lamont.columbia.edu/" target="_blank" rel="noopener noreferrer" class="logo-link">
            <img :src="LDEOLogo" alt="Lamont-Doherty Earth Observatory" class="partner-logo" />
          </a>
        </div>
      </div>
        
      <div class="footer-column">
        <h4>Funded By</h4>
        <div class="logo-grid">
          <a href="https://www.nsf.gov/awardsearch/show-award/?AWD_ID=2053169" target="_blank" rel="noopener noreferrer" class="logo-link">
            <img :src="NSFLogo" alt="National Science Foundation" class="partner-logo" />
          </a>
          <a href="https://www.ukri.org/" target="_blank" rel="noopener noreferrer" class="logo-link">
            <img :src="UKRILogo" alt="UKRI" class="partner-logo" />
          </a>
          <a href="https://www.ukri.org/councils/nerc/" target="_blank" rel="noopener noreferrer" class="logo-link">
            <img :src="NERCLogo" alt="NERC" class="partner-logo" />
          </a>
        </div>
      </div>
        
      <div class="footer-column">
        <h4>Powered By</h4>
        <div class="logo-stack">
          <a href="https://docs.hpc.shef.ac.uk/en/latest/stanage" target="_blank" rel="noopener noreferrer" class="logo-link">
            <img :src="StanageLogo" alt="Stanage HPC" class="partner-logo" />
          </a>
        </div>
        <p class="footer-text mt-3">
          SHIVER is powered by the University of Sheffield HPC Stanage.
        </p>
      </div>
        
      <div class="footer-column">
        <h4>Connect</h4>
        <div class="contact-info">
          <p class="footer-text">
            <strong><AppLink to="/people" class="text-link">SHIVER Project Team</AppLink> </strong><br>
            School of Geography and Planning<br>
            University of Sheffield, UK<br>
            <a href="mailto:shiver@sheffield.ac.uk" class="text-link">shiver@sheffield.ac.uk</a>
          </p>
        </div>

        <h4 class="mt-4">Resources</h4>
        <ul class="resource-links">
          <li>
            <a href="https://github.com/shiver-ice-velocity/SHIVER" target="_blank" rel="noopener noreferrer" class="text-link">
              Find us on GitHub
            </a>
          </li>
          <li>
            <AppLink to="/documentation/citation" class="text-link">How to cite</AppLink>
          </li>
        </ul>
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
  padding: 60px 20px 20px; /* Slightly more top padding for breathing room */
  margin-top: auto;
  font-family: system-ui, -apple-system, sans-serif;
}

.footer-content {
  max-width: 1200px; /* Widened slightly to accommodate 4 columns */
  margin: 0 auto 50px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 40px;
  align-items: start;
}

.footer-column {
  display: flex;
  flex-direction: column;
}

.footer-column h4 {
  text-transform: uppercase;
  font-size: 0.9rem;
  color: #5a9bd4;
  margin-top: 0;
  margin-bottom: 20px;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(90, 155, 212, 0.3);
  padding-bottom: 8px;
}

/* Logo Layouts */
.logo-stack {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.logo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.logo-link {
  display: inline-block;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.logo-link:hover {
  transform: translateY(-2px);
  opacity: 1;
}

.partner-logo {
  height: 55px; /* Standardized height */
  width: auto;
  object-fit: contain; /* Prevents stretching */
  background-color: white;
  padding: 10px;
  border-radius: 6px;
  opacity: 0.9;
}

/* Typography & Spacing */
.footer-text {
  font-size: 0.85rem;
  line-height: 1.6;
  color: #ccc;
  margin: 0 0 15px 0;
}

.footer-text strong {
  color: #fff;
}

.mt-3 { margin-top: 15px; }
.mt-4 { margin-top: 30px; }

/* Text Links */
.text-link {
  color: #5a9bd4;
  text-decoration: none;
  transition: color 0.2s ease;
}

.text-link:hover {
  color: #fff;
  text-decoration: underline;
}

.strong-link {
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.resource-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 0.85rem;
}

/* Copyright */
.copyright {
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 20px;
  font-size: 0.8rem;
  color: #888;
}

/* Responsive adjustments for smaller screens */
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .footer-column h4 {
    text-align: center;
  }

  .logo-stack, .logo-grid {
    align-items: center;
    justify-content: center;
  }
}
</style>