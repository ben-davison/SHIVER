<script setup>
import { ref } from 'vue';
import { RouterLink, RouterView } from 'vue-router'
import LoginOverlay from './components/LoginOverlay.vue'; // <--- NEW IMPORT

// 1. Check if user is already logged in (sessionStorage persists until tab close)
const isAuthenticated = ref(sessionStorage.getItem('shiver_auth') === 'true');

// 2. Handle successful login
const handleLogin = () => {
  isAuthenticated.value = true;
  sessionStorage.setItem('shiver_auth', 'true');
};
</script>

<template>
  <LoginOverlay v-if="!isAuthenticated" @login-success="handleLogin" />

  <div v-else class="app-container">
    <header>
      <div class="wrapper">
        <RouterLink to="/" class="brand-link">
		  <img src="/logo/SHIVER_logo_sideview.svg" alt="SHIVER Logo" class="brand-logo" />
          <span>SHIVER</span>
        </RouterLink>

        <nav>
          <RouterLink to="/" active-class="active-link">Home</RouterLink>
          <RouterLink to="/map" active-class="active-link">Explore Data</RouterLink>
		  <RouterLink to="/documentation" active-class="active-link">Documentation</RouterLink>
		  <RouterLink to="/fram" active-class="active-link">FRAM Project</RouterLink>
		  <RouterLink to="/people" active-class="active-link">People</RouterLink>
        </nav>
      </div>
    </header>

    <RouterView />
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
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2); /* Subtle shadow for depth */
  z-index: 2000; /* High z-index to stay above the map */
  position: relative;
}

.wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
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
.brand-link span {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
}

/* --- NAVIGATION --- */
nav {
  font-size: 1rem;
}

nav a {
  color: #e1e8ed; /* Light grey-blue */
  text-decoration: none;
  margin-left: 25px;
  font-weight: 600;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent; /* Reserve space for hover line */
  transition: all 0.2s;
}

nav a:hover {
  color: white;
  border-bottom-color: rgba(255, 255, 255, 0.5);
}

/* Styles for the currently active page (added automatically by Vue Router) */
.active-link {
  color: white;
  border-bottom-color: #0056b3; /* SHIVER Blue highlight */
}
</style>