<script setup>
import { ref } from 'vue';
import { RouterLink, RouterView } from 'vue-router'
import LoginOverlay from './components/LoginOverlay.vue'; 
import CookieBanner from './components/CookieBanner.vue'; // Import it here

// 1. Check if user is already logged in (sessionStorage persists until tab close)
const isAuthenticated = ref(sessionStorage.getItem('shiver_auth') === 'true');

// 2. Handle successful login
const handleLogin = () => {
  isAuthenticated.value = true;
  sessionStorage.setItem('shiver_auth', 'true');
};

// --- MOBILE MENU LOGIC ---
const isMenuOpen = ref(false);

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

// Close menu when a link is clicked (UX best practice)
const closeMenu = () => {
  isMenuOpen.value = false;
};

</script>

<template>
  <LoginOverlay v-if="!isAuthenticated" @login-success="handleLogin" />

  <div v-else class="app-container">
    <header>
      <div class="wrapper">
        <RouterLink to="/" class="brand-link" @click="closeMenu">
          <img src="/logo/SHIVER_logo_sideview.svg" alt="SHIVER Logo" class="brand-logo" />
          <span class="brand-text">SHIVER</span>
        </RouterLink>

        <nav class="desktop-nav">
          <RouterLink to="/" active-class="active-link">Home</RouterLink>
          <RouterLink to="/map" active-class="active-link">Explore Data</RouterLink>
          <RouterLink to="/documentation" active-class="active-link">Documentation</RouterLink>
          <RouterLink to="/fram" active-class="active-link">FRAM Project</RouterLink>
          <RouterLink to="/people" active-class="active-link">People</RouterLink>
        </nav>

        <button class="hamburger-btn" @click="toggleMenu" :class="{ 'open': isMenuOpen }">
          <span class="bar"></span>
          <span class="bar"></span>
          <span class="bar"></span>
        </button>
      </div>
	  
	  <transition name="slide">
        <div v-if="isMenuOpen" class="mobile-menu">
          <RouterLink to="/" active-class="active-link" @click="closeMenu">Home</RouterLink>
          <RouterLink to="/map" active-class="active-link" @click="closeMenu">Explore Data</RouterLink>
          <RouterLink to="/documentation" active-class="active-link" @click="closeMenu">Documentation</RouterLink>
          <RouterLink to="/fram" active-class="active-link" @click="closeMenu">FRAM Project</RouterLink>
          <RouterLink to="/people" active-class="active-link" @click="closeMenu">People</RouterLink>
        </div>
      </transition>
    </header>

    <RouterView />
	
	<CookieBanner />
  </div>
</template>

<style>
/* GLOBAL RESET: Removes default white margins from the browser body */
body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden; /* Prevent horizontal scroll */
}
</style>

<style scoped>
/* --- APP LAYOUT --- */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* --- HEADER BAR --- */
header {
  background-color: #0b1e3b; /* Matches the HomeView Footer & Hero fallback */
  height: 60px; /* Fixed height to match MapView calculation */
  width: 100%;
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2); /* Subtle shadow for depth */
  z-index: 2000; /* High z-index to stay above the map */
  position: relative;
}

.wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* --- BRANDING --- */
.brand-link {
  display: flex;           /* Aligns logo and text side-by-side */
  align-items: center;     /* Centers them vertically */
  gap: 12px;               /* Adds space between logo and text */
  text-decoration: none;   /* Removes underline */
  color: white;
  transition: opacity 0.2s;
  z-index: 2002; /* Ensure logo stays above mobile menu */
}

.brand-link:hover {
  opacity: 0.8;
}

/* Optional: Control logo size specifically */
.brand-logo {
  height: 32px;            /* Good size for a 60px header */
  width: auto;             /* Keeps aspect ratio */
}

/* Style the text specifically if needed */
.brand-text {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
  white-space: nowrap;
}

/* --- NAVIGATION --- */
.desktop-nav {
  /* Restore the font-size here */
  font-size: 1rem;
}

/* --- DESKTOP NAV --- */
.desktop-nav a {
  color: #e1e8ed;
  text-decoration: none;
  margin-left: 25px;
  font-weight: 600;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.desktop-nav a:hover {
  color: white;
  border-bottom-color: rgba(255, 255, 255, 0.5);
}

/* Styles for the currently active page (added automatically by Vue Router) */
.active-link {
  color: white !important;
  border-bottom-color: #0056b3 !important;
}

/* --- HAMBURGER BUTTON (Hidden by default) --- */
.hamburger-btn {
  display: none; /* Hidden on desktop */
  background: none;
  border: none;
  cursor: pointer;
  flex-direction: column;
  gap: 5px;
  padding: 5px;
  z-index: 2002;
  margin-right: 25px;
}

.bar {
  display: block;
  width: 25px;
  height: 3px;
  background-color: white;
  border-radius: 2px;
  transition: 0.3s;
}

/* --- MOBILE MENU DROPDOWN --- */
.mobile-menu {
  position: absolute;
  top: 60px; /* Directly below the header */
  left: 0;
  width: 100%;
  background-color: #0b1e3b;
  display: flex;
  flex-direction: column;
  padding: 10px 0 20px 0;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  z-index: 2001;
}

.mobile-menu a {
  color: #e1e8ed;
  text-decoration: none;
  padding: 15px 20px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: center;
}

.mobile-menu a:hover {
  background-color: rgba(255,255,255,0.05);
  color: white;
}

/* --- RESPONSIVE MEDIA QUERY --- */
/* Trigger at 768px (standard tablet width) */
@media (max-width: 768px) {
  /* 1. Hide the SHIVER text */
  .brand-text {
    display: none;
  }

  /* 2. Hide Desktop Navigation */
  .desktop-nav {
    display: none;
  }

  /* 3. Show Hamburger Button */
  .hamburger-btn {
    display: flex;
  }
}

/* --- ANIMATIONS --- */
/* Simple slide down animation for the menu */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 300px;
  opacity: 1;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0; /* Collapse padding too */
}

</style>