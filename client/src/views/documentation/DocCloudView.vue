<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// Handles URL hash jumping on first load
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
    
    <section id="cloud">
      <h2>Cloud Data Access</h2>
	  <p>
          All of the data provided through the SHIVER GUIs are available programmatically via <AppLink to="https://source.coop/" target="_blank" rel="noopener" class="text-link">Source Cooperative</AppLink>
	  </p>
	  <p>
		  For details of how to access these data, please see our ReadTheDocs page (<AppLink to="https://shiver-zarr.readthedocs.io/" target="_blank" rel="noopener" class="text-link">https://shiver-zarr.readthedocs.io/</AppLink>), which provides several examples of how to access these data programmatically.
	  </p>
    </section>

  </div>
</template>



// ----- CSS ---- //
<style scoped>


.citation-block {
  background: #f5f5f5;
  padding: 20px;
  font-family: 'Courier New', Courier, monospace;
  border-radius: 6px;
  border: 1px solid #ddd;
}


</style>