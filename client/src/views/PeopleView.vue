<script setup>
/**
 * PEOPLE VIEW
 * Displays the team in a responsive grid layout.
 */

// --- 1. IMPORT FOOTER LOGOS ---
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';

// --- 2. IMPORT TEAM PHOTOS ---
import photoBenD from '../assets/people/BenDavison.jpg';

// For now, I will use a placeholder function so the code runs immediately
const getPlaceholderUrl = (name) => `https://ui-avatars.com/api/?name=${name}&background=0D8ABC&color=fff&size=200`;

// --- 3. TEAM DATA ---
const teamMembers = [
  {
    id: 1,
    name: "Prof. Jonathan Kingslake",
    role: "FRAM Principal Investigator",
	institution: "Lamont-Doherty Earth Observatory",
    // image: photoAlice, // <--- Use the imported variable here later
    image: getPlaceholderUrl("Jonny+Kingslake"), 
    bio: "Jonny leads the FRAM project. They specialise in ApRES measurements and Antarctic surface hydrology."
  },
  {
    id: 2,
    name: "Prof. Andrew Sole",
    role: "FRAM Co-Investigator (UK Lead)",
	institution: "University of Sheffield",
    image: getPlaceholderUrl("Andrew+Sole"),
    bio: "Andrew leads the UK side of the FRAM project and led the development of SCADI. They specialise in remote sensing of glacier dynamics and interactions between meltwater and ice motion."
  },
  {
    id: 3,
    name: "Isabel Cordero",
    role: "Logistics manager",
	institution: "Lamont-Doherty Earth Observatory",
    image: getPlaceholderUrl("Isabel+Cordero"),
    bio: "Isabel makes sure everyone and everything gets where it needs to be when it needs to be there."
  },
  {
    id: 4,
    name: "Dr. Ben Davison",
    role: "Postdoctoral Research Associate",
	institution: "University of Sheffield",
    image: photoBenD,
    bio: "Ben leads the remote sensing project work, including SCADI optimization and automation and SHIVER development. They deployed GNSS, ApRES and a passive seismometer during the 2024 field season."
  },
  {
    id: 5,
    name: "Dr. Jeremy Ely",
    role: "Co-Investigator",
	institution: "University of Sheffield",
    image: getPlaceholderUrl("Jeremy+Ely"),
    bio: "Jeremy is an expert in glacial geomorphology and hydrology. They help us to interpret our field and satellite observations, and provide guidance on key science questions."
  },
  {
    id: 6,
    name: "Nick Frearson",
    role: "Logistics support",
	institution: "Lamont-Doherty Earth Observatory",
    image: getPlaceholderUrl("Nick+Frearson"),
    bio: "If it's broken, Nick can fix it."
  },
  {
    id: 7,
    name: "Dr. Andrew Hoffman",
    role: "Postdoctoral Research Associate",
	institution: "Lamont-Doherty Earth Observatory",
    image: getPlaceholderUrl("Andrew+Hoffman"),
    bio: "Andrew is a glacial geophysics and fieldwork specialist. They deployed GNSS and ApRES during the 2025 field season."
  },
  {
    id: 8,
    name: "Prof. Stephen Livingstone",
    role: "Co-Investigator",
	institution: "University of Sheffield",
    image: getPlaceholderUrl("Stephen+Livingstone"),
    bio: "Stephen is an expert in subglacial lakes. They help us to interpret our field and satellite observations, and provide guidance on key science questions."
  },
  {
    id: 9,
    name: "Sian Thorpe",
    role: "Research Associate",
	institution: "University of Sheffield",
    image: getPlaceholderUrl("Sian+Thorpe"),
    bio: "Sian is an expert in subglacial lake dynamics and glacial fieldwork. They support the SCADI remote sensing and deployed GNSS and a passive seismometer during the 2025 field season."
  },
  {
    id: 10,
    name: "Dr. Rohi Muthyala",
    role: "Postdoctoral Research Associate",
	institution: "Lamont-Doherty Earth Observatory",
    image: getPlaceholderUrl("Rohi+Muthyala"),
    bio: "Rohi is a hydrologist and field glaciologist. They deployed an AWS and piloted the UAV during the 2024 and 2025 field seasons."
  },
  {
    id: 11,
    name: "Dr. Kate Winter",
    role: "Co-Investigator",
	institution: "Northumbria University",
    image: getPlaceholderUrl("Kate+Winter"),
    bio: "Kate is a glacial geophysics expert. They deployed GNSS and ApRES during the 2024 field season."
  }
];
</script>

<template>
  <div class="page-container">
    
    <main class="content-wrapper">
      <div class="header-section">
        <h1>Meet the Team</h1>
        <p class="subtitle">The researchers behind FRAM and SHIVER</p>
      </div>

      <div class="team-grid">
        <div v-for="person in teamMembers" :key="person.id" class="person-card">
          <div class="image-wrapper">
            <img :src="person.image" :alt="person.name" class="profile-pic" />
          </div>
          <div class="card-content">
            <h3 class="person-name">{{ person.name }}</h3>
            <div class="person-role">{{ person.role }}</div>
			<div class="person-institution">{{ person.institution }}</div>
            <p class="person-bio">{{ person.bio }}</p>
          </div>
        </div>
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
        &copy; {{ new Date().getFullYear() }} SHIVER Project. Licensed under MIT/GNU GPL.
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
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 60px 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 60px;
}

h1 {
  font-size: 3rem;
  color: #0b1e3b;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.3rem;
  color: #5a9bd4;
  font-weight: 300;
  margin-top: 0;
}

/* --- GRID SYSTEM --- */
.team-grid {
  display: grid;
  /* Auto-fit magic: Creates as many columns as fit, but no smaller than 280px */
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 40px;
  justify-content: center;
}

/* --- PERSON CARD --- */
.person-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 30px;
}

.person-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.image-wrapper {
  width: 150px;
  height: 150px;
  margin-bottom: 20px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #f0f8ff;
}

.profile-pic {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ensures image fills circle without stretching */
}

.person-name {
  color: #0b1e3b;
  margin: 0 0 5px 0;
  font-size: 1.4rem;
}

.person-role {
  color: #0056b3;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 1px;
  margin-bottom: 5px;
}

.person-institution {
  color: #6c757d;     
  font-size: 0.9rem;  
  font-weight: 500;   
  font-style: italic;  
  margin-bottom: 15px; 
}

.person-bio {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* --- FOOTER (Standardized) --- */
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
  color: #5a9bd4;
  margin-bottom: 15px;
  text-transform: uppercase;
  font-size: 0.9rem;
}

.partner-logo {
  height: 60px;
  width: auto;
  background: white;
  padding: 8px;
  border-radius: 6px;
}

.copyright {
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 20px;
  font-size: 0.8rem;
  color: #888;
}
</style>