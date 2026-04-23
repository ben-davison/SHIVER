<template>
  <div class="auth-page">
    <div class="auth-box">
      <h2>Access Data Cubes</h2>
      <p>Please log in to access all SHIVER functions.</p>
      
      <form @submit.prevent="handleLogin">
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Password" required />
        
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Log In' }}
        </button>
        
        <p v-if="error" class="error">{{ error }}</p>
      </form>
      
      <div class="footer">
        Don't have an account? <router-link to="/register">Register here</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const auth = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    await auth.login(email.value, password.value);
    router.push('/cube'); // Redirect to CubeView after login
  } catch (e) {
    error.value = 'Invalid credentials';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  height: calc(100vh - 60px);
  background: #0b1e3b;
  display: flex;
  justify-content: center;
  align-items: center;
}
.auth-box {
  background: #15294a;
  padding: 40px;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  text-align: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
input {
  width: 100%;
  padding: 12px;
  margin: 10px 0;
  background: #0b1e3b;
  border: 1px solid #2c3e50;
  color: white;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 12px;
  background: #00ccff;
  border: none;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  border-radius: 4px;
}
.error { color: #ff6b6b; margin-top: 10px; }
.footer { margin-top: 20px; font-size: 0.9rem; color: #ccc; }
.footer a { color: #00ccff; text-decoration: none; }
</style>