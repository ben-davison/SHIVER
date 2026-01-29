<script setup>
import { ref } from 'vue';

const password = ref('');
const error = ref(false);
const isLoading = ref(false); // Add a loading state
const emit = defineEmits(['login-success']);

// Get the API URL from the environment (defined in .env.production)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const checkLogin = async () => {
  error.value = false;
  isLoading.value = true;

  try {
    // Send the password to your PC to be checked
    const response = await fetch(`${API_URL}/api/auth`, {
	  method: 'POST',
	  headers: { 
		'Content-Type': 'application/json',
		'ngrok-skip-browser-warning': 'true' // <--- ADD THIS LINE
	  },
	  body: JSON.stringify({ password: password.value })
	});

    if (response.ok) {
      emit('login-success');
    } else {
      error.value = true; // 401 Unauthorized
    }
  } catch (e) {
    console.error("Login Error:", e);
    error.value = true;
    alert("Could not connect to the server. Is your PC/Ngrok running?");
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="overlay">
    <div class="login-box">
      <h2>SHIVER Beta Access</h2>
      <p>Please enter the project access code.</p>
      
      <input 
        type="password" 
        v-model="password" 
        @keyup.enter="checkLogin" 
        placeholder="Enter password"
      />
      <button @click="checkLogin" :disabled="isLoading">
		  {{ isLoading ? 'Checking...' : 'Enter' }}
	  </button>
      
      <p v-if="error" class="error">Incorrect password</p>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(11, 30, 59, 0.98); /* Matches your SHIVER Navy */
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.login-box { background: white; padding: 40px; border-radius: 8px; text-align: center; }
input { padding: 10px; margin-right: 10px; border: 1px solid #ccc; border-radius: 4px;}
button { padding: 10px 20px; background: #0b1e3b; color: white; border: none; border-radius: 4px; cursor: pointer; }
.error { color: red; margin-top: 10px; }
</style>