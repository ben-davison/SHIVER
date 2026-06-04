<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import ProjSectionCard from '../../components/ProjSectionCard.vue' 

const route = useRoute()

// Standard hash jumping on first load
onMounted(() => {
  if (route.hash) {
    nextTick(() => {
      setTimeout(() => {
        const element = document.getElementById(route.hash.slice(1))
        if (element) {
          const headerOffset = 100;
          const elementPosition = element.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.scrollY - headerOffset;
          window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
      }, 100)
    })
  }
})
</script>

<template>
  <div class="doc-inner-page">
    
    <section id="introduction">
      <h1>SHIVER Projects Overview</h1>
      <p class="intro-text">
        <strong>SHIVER</strong> and <strong>SHIFT</strong> have benefitted from support from several projects.
		Learn more about those projects below.
      </p>
    </section>

    <section class="overview-cards-container">
      
      <ProjSectionCard 
        title="FRAM: Flow Response of Antarctica to Meltwater" 
        to="https://ldeo-glaciology.github.io/AntPen_NSF_NERC/"
      >
        <template #image>
          <img src="../../assets/projects/overview/fram_thumb.png" alt="FRAM logo">
        </template>
        <template #description>
          <p>
            The FRAM project combined fieldwork and remote sensing to determine whether meltwater directly affects the velocity 
		    of Antarctic Peninsula outlet glaciers, how widespread it is and how important it is on annual timescales.
          </p>
		  
          <p>
            FRAM is jointly funded by the UK Natural Environment Research Council (NERC) and the US National Science Foundation (NSF). 
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
		  
		  <p>
            The remote sensing component of the FRAM project involved automating the SHIFT processing and developing the first
			version of SHIVER to enable quick and easy exploration of seasonal speed changes on the Antarctic Peninsula.
          </p>
		  
		  <br>
		  
        </template>
      </ProjSectionCard>




	  <ProjSectionCard
        title="SLIDE: Subglacial Lakes at Isunguata Sermia - Dynamics and Evolution" 
        to="https://the-slide-project.github.io/index"
      >
        <template #image>
          <img src="../../assets/projects/overview/slide_thumb.png" alt="FRAM logo">
        </template>
        <template #description>
          <p>
            This three year project aims to determine how water is stored in lakes under the Greenland Ice Sheet, 
			how they drain and evolve through time, and their wider impact on water drainage and the flow of ice.
          </p>
		  
		  <p>
            In SLIDE, the SHIFT output was used to assess the ice velocity response to subglacial and ice-marginal
			lake drainage.
          </p>
		  
        </template>
      </ProjSectionCard>



    </section>

  </div>
</template>

<style scoped>
/* Minor spacing adjustment for the container */
.overview-cards-container {
  margin-top: 40px;
  display: flex;
  flex-direction: column;
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

</style>