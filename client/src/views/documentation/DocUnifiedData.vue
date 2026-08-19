<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const docContent = ref('<p>Loading Unified Data documentation...</p>');

onMounted(async () => {
  // 1. Point to the specific RTD page
  const rtdUrl = encodeURIComponent(
    'https://shiver-zarr.readthedocs.io/en/latest/zarr_data/unified_data.html'
  );
  const apiUrl = `https://app.readthedocs.org/api/v3/embed/?url=${rtdUrl}`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) throw new Error('Failed to fetch RTD content');
    
    const data = await response.json();
    docContent.value = data.content;

    // 2. CRITICAL: Handle scrolling if the user navigated directly to a hash URL
    if (route.hash) {
      // Wait for Vue to render the newly fetched HTML into the DOM
      await nextTick();
      
      // Add a tiny timeout to ensure the browser has painted the injected HTML
      setTimeout(() => {
        const sectionId = route.hash.slice(1);
        const element = document.getElementById(sectionId);
        
        if (element) {
          const headerOffset = 100; // Matches your layout's sticky header
          const elementPosition = element.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.scrollY - headerOffset;
          
          window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
        }
      }, 100);
    }

  } catch (error) {
    console.error(error);
    docContent.value = '<p>Error loading documentation. Please check your connection or visit the main docs site.</p>';
  }
});
</script>

<template>
  <section class="rtd-injected-content" v-html="docContent"></section>
</template>


<style scoped>
/* 
  1. Fix the Image Sizes 
  Forces all images to never exceed the width of their container, 
  and maintains their aspect ratio.
*/
.rtd-injected-content :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
}

/* 
  2. Hide the Sphinx Headerlinks 
  Hides the "#" symbols that appear when hovering over headers.
*/
.rtd-injected-content :deep(.headerlink) {
  display: none !important;
}

/* 
  3. Hide the Top Toolbar 
  Hides the GitHub, download, and light/dark mode buttons.
*/
.rtd-injected-content :deep(.bd-header-article),
.rtd-injected-content :deep(.article-header-buttons) {
  display: none !important;
}

/* 
  4. Hide the Right-Hand Contents Menu 
  Hides the in-page TOC that usually sits on the right.
*/
.rtd-injected-content :deep(.bd-sidebar-secondary),
.rtd-injected-content :deep(.toc-item) {
  display: none !important;
}

/* 
  5. Hide the Next / Previous Buttons 
  Hides the bottom navigation blocks.
*/
.rtd-injected-content :deep(.prev-next-area),
.rtd-injected-content :deep(.related) {
  display: none !important;
}

/* Optional: Clean up code block styling if needed */
.rtd-injected-content :deep(pre) {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
}

/*
  6. Hide the extra title and contents
*/
.rtd-injected-content :deep(#jb-print-docs-body),
.rtd-injected-content :deep(.onlyprint) {
  display: none !important;
}
</style>