<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import DocSectionCard from '../../components/DocSectionCard.vue' 
import DocSectionCardShort from '../../components/DocSectionCardShort.vue' 
// -----------------------------------------------------------------------------------------
// --- SEO ---------------------------------------------------------------------------------
import { useHead } from '@unhead/vue'
useHead({
  title: 'SHIVER | Documentation',
  meta: [
    { 
      name: 'description', 
      content: 'Welcome to the technical documentation for SHIFT (SHeffield Ice Flow Tracker) and SHIVER (SHeffield Ice Velocity ExploreR). Select a section below to explore our methodology, data sources, and interactive tools.' 
    }
  ]
})


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
      <h1>Documentation Overview</h1>
      <p class="intro-text">
        Welcome to the technical documentation for <strong>SHIFT</strong> (SHeffield Ice Flow Tracker) 
        and <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR). Select a section below to explore 
        our methodology, data sources, and interactive tools.
      </p>
    </section>

    <section class="overview-cards-container">
      
      <DocSectionCardShort 
        title="Greenland Data Sources" 
        to="/documentation/greenland"
      >
        <template #image>
          <img src="../../assets/documentation/overview/greenland_thumb.png" alt="Map of Greenland">
        </template>
        <template #description>
          <p>
            This page provides details of all data sources contributing to our Greenland data cube.
          </p>
        </template>
      </DocSectionCardShort>
	  
	  <DocSectionCardShort 
        title="Antarctic Data Sources" 
        to="/documentation/antarctic"
      >
        <template #image>
          <img src="../../assets/documentation/overview/antarctica_thumb.png" alt="Map of Antarctica">
        </template>
        <template #description>
          <p>
            This page provides details of all data sources contributing to our Antarctic data cube.
          </p>
        </template>
      </DocSectionCardShort>

      <DocSectionCard 
        title="SHIFT Algorithms" 
        to="/documentation/shift"
      >
        <template #image>
          <img src="../../assets/documentation/CC.jpg" alt="SHIFT Diagram">
        </template>
        <template #description>
          <p>
            This page provides technical documentation for <strong>SHIFT</strong> (SHeffield Ice Flow Tracker).
            SHIFT is the processing pipeline we use to derive velocity fields from Sentinel-1 Synthetic Aperture Radar (SAR) image pairs.
          </p>
        </template>
      </DocSectionCard>
	  
	  <DocSectionCardShort 
        title="Data Cube Generation" 
        to="/documentation/datacubegen"
      >
        <template #image>
          <img src="../../assets/documentation/zarr/zarr.png" alt="Zarr logo">
        </template>
        <template #description>
          <p>
            This page describes our ice velocity data cubes - what they are and how we create them.
          </p>
        </template>
      </DocSectionCardShort>

      <DocSectionCard 
        title="SHIVER Timeseries Explorer" 
        to="/documentation/timeseriesexplore"
      >
        <template #image>
          <img src="../../assets/documentation/overview/timeseries_thumb.png" alt="Timeseries graph">
        </template>
        <template #description>
          <p>
            This page provides detailed documentation for <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR).
            SHIVER allows you to explore and download a multitude of ice velocity measurements for Greenland and Antarctica using one simple interface.
          </p>
        </template>
      </DocSectionCard>
	  
	  <DocSectionCard 
        title="Cloud Data Access" 
        to="/documentation/cloud"
      >
        <template #image>
          <img src="../../assets/documentation/overview/source_logo.png" alt="Source Cooperative logo">
        </template>
        <template #description>
          <p>
            This page provides a summary of how to access the <strong>SHIVER</strong> data programmatically.
            By accessing the data through the cloud, you can scale up and expand on any analysis or discoveries you've made in the application.
          </p>
        </template>
      </DocSectionCard>
	  
	  <DocSectionCardShort 
        title="Citation & License" 
        to="/documentation/citation"
      >
        <template #image>
          <img src="../../assets/documentation/overview/harvard_thumb.png" alt="Citation Image">
        </template>
        <template #description>
          <p>
            This page provides details of how to cite SHIFT, SHIVER and other datasets incorporated into our interface.
          </p>
        </template>
      </DocSectionCardShort>

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
</style>