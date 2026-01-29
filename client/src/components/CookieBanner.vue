<template>
  <div v-if="isOpen" class="cookie-banner">
    <div class="cookie-content">
      <h3>We use cookies</h3>
      <p>
        We use cookies to analyze traffic and improve your experience. 
        You can accept analytics cookies or use the site without them.
      </p>
    </div>
    <div class="cookie-buttons">
      <button @click="acceptCookies" class="btn-accept">Accept</button>
      <button @click="declineCookies" class="btn-decline">Decline</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const isOpen = ref(false);
const GA_MEASUREMENT_ID = "G-4YGWRB6RCZ";

// Helper: Load Google Analytics Manually
const loadGoogleAnalytics = () => {
  // Prevent duplicate loading
  if (document.querySelector(`script[src*="${GA_MEASUREMENT_ID}"]`)) return;

  const script = document.createElement('script');
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  script.async = true;
  document.head.appendChild(script);

  // We must attach dataLayer and gtag to 'window' explicitly
  // so that MapView.vue can access them.
  window.dataLayer = window.dataLayer || [];
  
  window.gtag = function(){
    window.dataLayer.push(arguments);
  };

  window.gtag('js', new Date());
  window.gtag('config', GA_MEASUREMENT_ID);
  
  console.log("?? Google Analytics Loaded via Custom Component");
};

const acceptCookies = () => {
  localStorage.setItem('cookie_consent', 'accepted');
  loadGoogleAnalytics();
  isOpen.value = false;
};

const declineCookies = () => {
  localStorage.setItem('cookie_consent', 'declined');
  isOpen.value = false;
};

onMounted(() => {
  const consent = localStorage.getItem('cookie_consent');
  
  if (consent === 'accepted') {
    // If they already accepted in the past, load GA immediately
    loadGoogleAnalytics();
  } else if (!consent) {
    // If no choice made yet, show banner
    isOpen.value = true;
  }
});
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  bottom: 20px;
  left: 20px;
  right: 20px; /* Or max-width for a smaller box */
  max-width: 400px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 9999;
  border: 1px solid #eee;
  font-family: sans-serif;
}

.cookie-content h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.1rem;
  color: #333;
}

.cookie-content p {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 20px;
  line-height: 1.4;
}

.cookie-buttons {
  display: flex;
  gap: 10px;
}

button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}

.btn-accept {
  background-color: #2b2b2b;
  color: white;
}

.btn-decline {
  background-color: #f0f0f0;
  color: #333;
}

button:hover {
  opacity: 0.9;
}
</style>