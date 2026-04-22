<script setup>
import { ref } from 'vue'

const props = defineProps({
  caption: {
    type: String,
    default: ''
  }
})

const isOpen = ref(false)
const modalSrc = ref('')

// This clever trick grabs the fully processed image URL directly 
// from the clicked image, so Vite's path resolution doesn't break!
const openModal = (event) => {
  if (event.target.tagName === 'IMG') {
    modalSrc.value = event.target.src;
    isOpen.value = true;
  }
}
</script>

<template>
  <figure class="zoomable-figure">
    <div class="image-wrapper" @click="openModal" title="Click to enlarge">
      <slot></slot>
    </div>
    
    <figcaption v-if="caption" class="figure-caption">
      {{ caption }}
    </figcaption>
  </figure>

  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click="isOpen = false">
      <button class="close-btn" @click="isOpen = false">&times;</button>
      
      <div class="modal-content" @click.stop>
        <img :src="modalSrc" class="modal-image" alt="Enlarged view" />
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* --- INLINE FIGURE STYLES --- */
.zoomable-figure {
  text-align: center;
  margin: 40px 0;
}

.image-wrapper {
  display: inline-block;
  cursor: zoom-in; /* Shows a magnifying glass cursor */
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-wrapper:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* This targets the <img> tag you place inside the slot */
.image-wrapper :deep(img) {
  max-width: 100%;
  display: block; /* Fixes tiny white space below images */
}

.figure-caption {
  font-size: 0.95rem;
  color: #666;
  margin-top: 10px;
  font-style: italic;
}

/* --- FULL-SCREEN MODAL STYLES --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(11, 30, 59, 0.9); /* A nice dark blue tint matching your theme */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; 
  cursor: zoom-out;
}

.modal-content {
  max-width: 95vw;
  max-height: 95vh;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: default; 
}

.modal-image {
  max-width: 100%;
  max-height: 95vh;
  border-radius: 4px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 30px;
  background: none;
  border: none;
  color: white;
  font-size: 40px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}
</style>