<template>
  <div v-if="isOpen" class="video-modal-overlay" @click.self="$emit('close')">
    <div class="video-modal-content">
      <div class="video-modal-header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="video-modal-body">
        <iframe 
          class="tutorial-video" 
          :src="videoSrc" 
          title="YouTube video player" 
          frameborder="0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
          allowfullscreen>
        </iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isOpen: Boolean,
  title: String,
  videoSrc: String
});
defineEmits(['close']);
</script>

<style scoped>
.video-modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex; justify-content: center; align-items: center;
  z-index: 9999; /* Sit on top of everything */
}
.video-modal-content {
  background: #fff; padding: 20px; border-radius: 8px;
  width: 90%; max-width: 800px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.video-modal-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;
}
.video-modal-header h3 { margin: 0; color: #333; }
.close-btn { 
  background: none; border: none; font-size: 28px; cursor: pointer; color: #666; 
}
.close-btn:hover { color: #000; }
.video-modal-body { position: relative; padding-top: 56.25%; /* 16:9 Aspect Ratio */ }
.tutorial-video {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 4px;
}
</style>