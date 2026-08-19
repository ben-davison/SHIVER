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
        Welcome to the technical documentation for <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR). Select a section below to explore 
        our methodology, data and interactive tools.
      </p>
    </section>

    <section class="overview-cards-container">
	
	  <DocSectionCardShort 
        title="Zarr Data" 
        to="/documentation/whatiszarr"
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
      
      <DocSectionCardShort 
        title="Contributing Datasets" 
        to="/documentation/contributingdata"
      >
        <template #image>
          <img src="../../assets/documentation/overview/antarctica_thumb.png" alt="Map of Antarctica">
        </template>
        <template #description>
          <p>
            This page provides details of all the contributing datasets incorporated into our unified dataset.
          </p>
        </template>
      </DocSectionCardShort>
	  
	  <DocSectionCardShort 
        title="Unified Datasets" 
        to="/documentation/unifieddata"
      >
        <template #image>
          <img src="../../assets/documentation/overview/raster_stack.png" alt="Raster Stack schematic">
        </template>
        <template #description>
          <p>
            This page provides details of our unified dataset.
          </p>
        </template>
      </DocSectionCardShort>

      <DocSectionCard 
        title="Dataset Comparison" 
        to="/documentation/datacomparison"
      >
        <template #image>
          <img src="../../assets/documentation/overview/ensemble_range.png" alt="Velocity difference overview">
        </template>
        <template #description>
          <p>
            This page summarises the differences in speed estimates during overlapping time periods between each of the Contributing Datasets
			after they have been incorporated into our Unified Dataset. The comparisons show that, on the whole, the datasets closely agree.
          </p>
        </template>
      </DocSectionCard>
	  
      <DocSectionCard 
        title="SHIVER Timeseries Explorer" 
        to="/documentation/timeseriesexplore"
      >
        <template #image>
          <img src="../../assets/documentation/overview/timeseries_thumb.png" alt="Timeseries graph">
        </template>
        <template #description>
          <p>
            This page provides detailed documentation for the <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR) Timeseries Explorer.
            The Explorer allows you to explore and download a multitude of ice velocity timeseries for Greenland and Antarctica using one simple interface.
          </p>
        </template>
      </DocSectionCard>
	  
	  <DocSectionCard 
        title="SHIVER NetCDF Extractor" 
        to="/documentation/netcdfextract"
      >
        <template #image>
          <img src="../../assets/images/NetCDF.png" alt="NetCDF logo">
        </template>
        <template #description>
          <p>
            This page provides detailed documentation for <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR) Data Cube Extractor.
            The Extractor allows you to extract and download a multitude of ice velocity measurements for Greenland and Antarctica over large areas and time periods using one simple interface.
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
        title="Citation" 
        to="/documentation/citation"
      >
        <template #image>
          <img src="../../assets/documentation/overview/harvard_thumb.png" alt="Citation Image">
        </template>
        <template #description>
          <p>
            This page provides details of how to cite SHIVER and other datasets incorporated into our Unified Dataset.
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