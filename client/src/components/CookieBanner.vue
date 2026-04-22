<template>
  <div v-if="isOpen" class="cookie-banner">
    <div class="cookie-content">
      <h3>Cookies are tasty. Please accept cookies</h3>
      <p>
        This allows us to use Google Analytics to track which of our SHIVER functions are being used.
        If you don't want cookies, please consider completing  
		<AppLink to="https://docs.google.com/forms/d/e/1FAIpQLSfsFX-w19UXjlVDpY7PeQlo0_482tHYPTVuatWup-B3OdZOrA/viewform?usp=publish-editor" target="_blank" rel="noopener" class="text-link">this short form</AppLink> 
		instead.
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
const EXPIRATION_DAYS = 7;
const EXPIRATION_MS = EXPIRATION_DAYS * 24 * 60 * 60 * 1000;

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
  const consentData = {
    value: 'accepted',
    timestamp: new Date().getTime()
  };
  localStorage.setItem('cookie_consent', JSON.stringify(consentData));
  loadGoogleAnalytics();
  isOpen.value = false;
};

const declineCookies = () => {
  const consentData = {
    value: 'declined',
    timestamp: new Date().getTime()
  };
  localStorage.setItem('cookie_consent', JSON.stringify(consentData));
  isOpen.value = false;
};

onMounted(() => {
  const consentString = localStorage.getItem('cookie_consent');
  
  if (consentString) {
    try {
      // Parse the JSON object
      const consent = JSON.parse(consentString);
      const now = new Date().getTime();
      
      // 1. Check if the consent has expired
      if (now - consent.timestamp > EXPIRATION_MS) {
        localStorage.removeItem('cookie_consent');
        isOpen.value = true; // Time is up, show the banner
        return;
      }

      // 2. If not expired, honor their choice
      if (consent.value === 'accepted') {
        loadGoogleAnalytics();
      }
      
    } catch (error) {
      // 3. Fallback: Catching old string formats
      // If a user has the old 'accepted' string saved, JSON.parse will fail.
      // This wipes the old format and shows the banner so they can save the new format.
      localStorage.removeItem('cookie_consent');
      isOpen.value = true;
    }
  } else {
    // No consent found at all, show banner
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