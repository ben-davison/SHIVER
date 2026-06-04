<script setup>
import { ref } from 'vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  to: {
    type: String,
    required: true
  }
})

// Tracks whether this specific card is expanded or truncated
const isExpanded = ref(false)
</script>

<template>
  <div class="doc-card">
    
    <div class="card-image">
      <a :href="to" target="_blank" rel="noopener">
        <slot name="image"></slot>
      </a>
    </div>

    <div class="card-content">
      <h2 class="card-title">
        <a :href="to" target="_blank" rel="noopener">{{ title }}</a>
      </h2>
      
      <div :class="['card-description', { 'is-expanded': isExpanded }]">
        <slot name="description"></slot>
      </div>
      
      <button class="expand-btn" @click="isExpanded = !isExpanded">
        {{ isExpanded ? 'Read less' : '... more' }}
      </button>
    </div>
    
  </div>
</template>

<style scoped>
/* Your existing CSS remains exactly the same! */
/* Because your styles targeted `.card-title a`, they will apply to the new <a> tag perfectly. */
.doc-card {
  display: flex;
  flex-direction: row;
  gap: 25px;
  background: #ffffff;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.doc-card:hover {
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}

.card-image {
  flex-shrink: 0;
  width: 220px; 
}

.card-image :deep(img) {
  width: 100%;
  height: 100%;
  aspect-ratio: 16 / 9;
  object-fit: contain;  
  border-radius: 6px;
  border: 1px solid #ddd;
  background-color: #fcfcfc;
  transition: opacity 0.2s;
}

.card-image :deep(img):hover {
  opacity: 0.85;
}

.card-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.card-title {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.card-title a {
  text-decoration: none;
  color: #0b1e3b;
  transition: color 0.2s;
}

.card-title a:hover {
  color: #0056b3;
}

.card-description {
  color: #555;
  line-height: 1.6;
  font-size: 1.05rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-description.is-expanded {
  -webkit-line-clamp: unset;
}

.expand-btn {
  align-self: flex-start;
  background: none;
  border: none;
  color: #0056b3;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 8px 0 0 0;
  cursor: pointer;
  transition: color 0.2s;
}

.expand-btn:hover {
  color: #0b1e3b;
  text-decoration: underline;
}

@media (max-width: 650px) {
  .doc-card {
    flex-direction: column;
  }
  .card-image {
    width: 100%;
  }
  .card-image :deep(img) {
    aspect-ratio: auto;
    max-height: 200px;
  }
}
</style>