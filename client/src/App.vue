<script setup>
import { ref, computed, onMounted, provide, watch } from 'vue';
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'
import UserLoginModal from './components/UserLoginModal.vue';
import CookieBanner from './components/CookieBanner.vue'; // Import it here
import AppFooter from './components/AppFooter.vue'; 

// --- USER LOGIN (Database Account) ---
// This checks if they have logged into their personal account
const isUserLoggedIn = ref(false);
const showUserLoginModal = ref(false);
const resetTokenToPass = ref(null);

// Check for user token on load
onMounted(() => {
    const token = sessionStorage.getItem('shiver_token');
    if (token) isUserLoggedIn.value = true;
});

const openLoginModal = () => {
  showUserLoginModal.value = true;
};

const handleUserLoginSuccess = () => {
    isUserLoggedIn.value = true;
    showUserLoginModal.value = false; // Close modal
};

// 3. Make this function available to ALL child components (like MapView)
provide('requireLogin', openLoginModal);

const handleLogout = () => {
    sessionStorage.removeItem('shiver_token');
    isUserLoggedIn.value = false;
    showUserLoginModal.value = false;
};


// --- Redirect to login or password reset if needed --- //
const route = useRoute();
const router = useRouter();
watch(
  () => route.query, 
  (currentQuery) => {
    // If there are no relevant query parameters, do nothing
    if (!currentQuery.login && !currentQuery.reset_token) return;

    let urlNeedsCleanup = false;
    const nextQuery = { ...currentQuery };

    // 1. Handle '?login=required'
    if (nextQuery.login === 'required') {
      openLoginModal();
      delete nextQuery.login;
      urlNeedsCleanup = true;
    }

    // 2. Handle '?reset_token=...'
    if (nextQuery.reset_token) {
      resetTokenToPass.value = nextQuery.reset_token;
      showUserLoginModal.value = true;
      delete nextQuery.reset_token;
      urlNeedsCleanup = true;
    }

    // 3. Clean up the URL in one single action
    if (urlNeedsCleanup) {
      // If we deleted all the keys, pass null to remove the '?' entirely
      const finalQuery = Object.keys(nextQuery).length > 0 ? nextQuery : null;
      router.replace({ query: finalQuery }).catch(() => {
        // Catching the promise prevents Vue Router from throwing harmless 
        // "Navigation cancelled" errors in the console during rapid redirects
      });
    }
  }, 
  { immediate: true } // Ensures this checks the URL immediately on page load
);

// --- 2. FOOTER VISIBILITY LOGIC --- //
// Hide the footer on fullscreen map interfaces
const showFooter = computed(() => {
  const hiddenRoutes = ['/map', '/cube']; 
  return !hiddenRoutes.includes(route.path);
});


// --- MOBILE MENU LOGIC ---
const isMenuOpen = ref(false);
const toggleMenu = () => {isMenuOpen.value = !isMenuOpen.value; };
const closeMenu = () => { isMenuOpen.value = false; };

</script>

<template>

  <div class="app-container">
    
    <UserLoginModal 
        v-if="showUserLoginModal" 
		:reset-token="resetTokenToPass"
        @close="showUserLoginModal = false; resetTokenToPass = null"
        @login-success="handleUserLoginSuccess"
    />

    <header>
      <div class="wrapper">
        <RouterLink to="/" class="brand-link" @click="closeMenu">
          <img src="/logo/SHIVER_logo_horizontal_v1_white_on_transparent_background_simplified.png" alt="SHIVER Logo" class="brand-logo" />
        </RouterLink>

        <nav class="desktop-nav">
          <RouterLink to="/" active-class="active-link">Home</RouterLink>
		  
          <div class="nav-dropdown">
				<RouterLink to="/map" class="dropdown-trigger" active-class="active-link">Explore Data</RouterLink>
				<div class="dropdown-content">
				  <RouterLink to="/map" active-class="active-sublink">Timeseries</RouterLink>
				  <RouterLink to="/cube" active-class="active-sublink">Data Cubes</RouterLink>
				</div>
          </div>
		  
          <div class="nav-dropdown">
				<RouterLink to="/documentation" class="dropdown-trigger" active-class="active-link" :class="{ 'active-link': $route.path.startsWith('/documentation') }">Documentation</RouterLink>
				<div class="dropdown-content">
				  <RouterLink to="/documentation/overview" active-class="active-sublink">Overview</RouterLink>
				  <RouterLink to="/documentation/greenland" active-class="active-sublink">Greenland Data</RouterLink>
				  <RouterLink to="/documentation/antarctic" active-class="active-sublink">Antarctic Data</RouterLink>
				  <RouterLink to="/documentation/shift" active-class="active-sublink">SHIFT Algorithms</RouterLink>
				  <RouterLink to="/documentation/datacubegen" active-class="active-sublink">Data Cube Generation</RouterLink>
				  <RouterLink to="/documentation/timeseriesexplore" active-class="active-sublink">SHIVER Timeseries Explorer</RouterLink>
				  <RouterLink to="/documentation/citation" active-class="active-sublink">Citation & License</RouterLink>
				</div>
		  </div>
		  
		  <div class="nav-dropdown">
				<RouterLink to="/projects" class="dropdown-trigger" active-class="active-link" :class="{ 'active-link': $route.path.startsWith('/projects') }">Projects</RouterLink>
		  </div>
		  
          <RouterLink to="/people" active-class="active-link">People</RouterLink>
        </nav>

        <div class="auth-controls">
            <RouterLink v-if="isUserLoggedIn" to="/profile" class="profile-link" title="My Profile">
                <svg class="user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span class="user-label">My Profile</span>
            </RouterLink>

            <button v-else id="btn-login" class="login-header-btn" @click="showUserLoginModal = true">
                Log In
            </button>

            <button class="hamburger-btn" @click="toggleMenu" :class="{ 'open': isMenuOpen }">
                <span class="bar"></span><span class="bar"></span><span class="bar"></span>
            </button>
        </div>
      </div>
      
      <transition name="slide">
        <div v-if="isMenuOpen" class="mobile-menu">
          <RouterLink to="/" active-class="active-link" @click="closeMenu">Home</RouterLink>
          
          <div class="mobile-group">
            <span class="mobile-group-title">Explore Data</span>
            <RouterLink to="/map" active-class="active-link" @click="closeMenu" class="mobile-sublink">Timeseries</RouterLink>
            <RouterLink to="/cube" active-class="active-link" @click="closeMenu" class="mobile-sublink">Data Cubes</RouterLink>
          </div>

          <RouterLink to="/documentation" active-class="active-link" @click="closeMenu">Documentation</RouterLink>
          <RouterLink to="/projects" active-class="active-link" @click="closeMenu">Projects</RouterLink>
          <RouterLink to="/people" active-class="active-link" @click="closeMenu">People</RouterLink>
            
          <div class="mobile-group">
             <span class="mobile-group-title">Account</span>
             
             <div v-if="isUserLoggedIn">
                 <RouterLink to="/profile" class="mobile-sublink" @click="closeMenu">My Profile</RouterLink>
                 <a href="#" class="mobile-sublink" @click.prevent="handleLogout(); closeMenu()">Log Out</a>
             </div>
             
             <div v-else>
                 <button class="mobile-login-btn" @click="()=>{ closeMenu(); showUserLoginModal = true; }">Log In</button>
             </div>
          </div>

        </div>
      </transition>
    </header>

    <RouterView />
	
	<CookieBanner />
	
	<AppFooter v-if="showFooter" />
	
  </div>
</template>

<style>
/* GLOBAL RESET: Removes default white margins from the browser body */
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  /* ... rest of your body styles ... */
}

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
  gap: 1px;               /* Adds space between logo and text */
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
  height: 48px;            /* Good size for a 60px header */
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
  margin-left: 15px;
  font-weight: 600;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.desktop-nav a:hover {
  color: white;
  border-bottom-color: rgba(255, 255, 255, 0.5);
}

.nav-dropdown {
  display: inline-block;
  position: relative;
}

/* 2. The Menu Box */
.dropdown-content {
  display: none; /* Hidden by default */
  position: absolute;
  top: 100%; 
  /* Align left edge with text (compensating for your existing margin-left: 25px) */
  left: 25px; 
  background-color: white;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  border-radius: 4px;
  z-index: 3000; /* High index to sit over the map */
  padding: 5px 0;
  margin-top: 5px; /* Slight gap below the nav line */
}

/* 3. Show on Hover */
.nav-dropdown:hover .dropdown-content {
  display: block;
}

/* 4. Dropdown Links (Professional & Complementary) */
.dropdown-content a {
  /* Reset styles so they don't look like main nav links */
  display: block;
  text-align: left;
  color: #2c3e50 !important; /* Dark text for readability */
  padding: 10px 15px;
  margin-left: 0 !important; /* Remove the main nav spacing */
  border-bottom: 1px solid #f1f1f1 !important; /* Subtle separator */
  font-size: 0.9rem; /* Smaller font as requested */
  font-weight: normal;
  text-decoration: none;
}

/* Last item needs no border */
.dropdown-content a:last-child {
  border-bottom: none !important;
}

/* Hover state for dropdown items */
.dropdown-content a:hover {
  background-color: #f8f9fa;
  color: #0056b3 !important; /* Brand blue on hover */
  border-bottom-color: #f1f1f1 !important; /* Keep border subtle */
}

/* Active state for sublinks */
.active-sublink {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #2c3e50;
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

.mobile-group {
  display: flex;
  flex-direction: column;
  width: 100%;
  /* Add a subtle divider above the group */
  border-top: 1px solid rgba(255,255,255,0.05); 
}

.mobile-group-title {
  /* CHANGED: Light Blue-Grey to be visible on Dark Blue */
  color: #8fa1b3; 
  font-size: 0.75rem; /* Slightly smaller label */
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 15px 0 5px 0;
  text-align: center; /* Keep it centered like your other links */
  font-weight: bold;
  opacity: 0.8;
}

.mobile-sublink {
  /* CHANGED: Remove heavy indent, use background distinction instead */
  padding-left: 20px !important; 
  padding-right: 20px !important;
  font-size: 0.95rem;
  /* Make sub-items slightly darker to show depth */
  background-color: rgba(0, 0, 0, 0.2); 
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: #e1e8ed;
}

/* Optional: distinct hover for sublinks */
.mobile-sublink:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

/* --- RESPONSIVE MEDIA QUERY --- */
/* Trigger at 768px (standard tablet width) */
@media (max-width: 950px) {
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
  
  .user-label { display: none; }
  .profile-link { padding: 8px; border-radius: 50%; }
    
   /* Or hide the header login button on mobile since it's in the menu */
   .login-header-btn { display: none; }
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

/* --- AUTH CONTROLS --- */
.auth-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 0 10px;
}

/* Login Button */
.login-header-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.4);
  color: white;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.login-header-btn:hover {
  background: white;
  color: #0b1e3b;
}

/* Profile Link */
.profile-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #e1e8ed;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.1);
  transition: background 0.2s;
  margin-right: 15px;
}

.profile-link:hover {
  background: rgba(255,255,255,0.2);
  color: white;
}

.user-icon {
  width: 18px;
  height: 18px;
  stroke: #e1e8ed; /* Light grey to match text */
}

/* Change icon color on hover */
.profile-link:hover .user-icon {
  stroke: white;
}

.user-label { display: block; }

/* Mobile Specifics */
.mobile-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 90%;
  margin: 10px auto;
  padding: 12px;
  background: #00ccff;
  border: none;
  color: #0b1e3b;
  font-weight: bold;
  border-radius: 4px;
}


</style>