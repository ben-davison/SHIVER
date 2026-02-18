<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { API_URL } from '../api';

const route = useRoute();
const router = useRouter();

const token = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const statusMsg = ref('');
const isSuccess = ref(false);
const isLoading = ref(false);

onMounted(() => {
  // Grab token from URL
  token.value = route.query.token;
  if (!token.value) {
    statusMsg.value = "Error: No reset token provided.";
  }
});

const handleReset = async () => {
  if (newPassword.value !== confirmPassword.value) {
    statusMsg.value = "Passwords do not match.";
    return;
  }
  
  isLoading.value = true;
  statusMsg.value = "";

  try {
    await axios.post(`${API_URL}/auth/reset-password`, {
      token: token.value,
      new_password: newPassword.value
    });
    
    isSuccess.value = true;
    statusMsg.value = "Password reset successfully! Redirecting...";
    
    setTimeout(() => {
      router.push('/');
    }, 3000);
    
  } catch (err) {
    statusMsg.value = err.response?.data?.detail || "Failed to reset password. Token may be invalid.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="reset-container">
    <div class="reset-box">
      <h2>Reset Password</h2>
      
      <div v-if="!isSuccess">
        <p class="instruction">Enter your new password below.</p>
        
        <form @submit.prevent="handleReset" class="reset-form">
          <label>New Password</label>
          <input type="password" v-model="newPassword" required placeholder="********" class="dark-input">
          
          <label>Confirm Password</label>
          <input type="password" v-model="confirmPassword" required placeholder="********" class="dark-input">
          
          <p v-if="statusMsg" class="error-text">{{ statusMsg }}</p>
          
          <button type="submit" class="submit-btn" :disabled="isLoading || !token">
             {{ isLoading ? 'Updating...' : 'Set New Password' }}
          </button>
        </form>
      </div>

      <div v-else class="success-view">
        <div class="check-icon">?</div>
        <p>{{ statusMsg }}</p>
        <button class="submit-btn" @click="router.push('/')">Go to Login</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 80vh; background: #0b1e3b; padding: 20px;
}
.reset-box {
  background: #1a2634; color: white; padding: 40px; border-radius: 8px;
  width: 100%; max-width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  text-align: center;
}
.reset-form { display: flex; flex-direction: column; gap: 15px; text-align: left; }
.dark-input {
  background: #0b1e3b; border: 1px solid #2c3e50; color: white;
  padding: 12px; border-radius: 4px; font-size: 1rem;
}
.submit-btn {
  background: #00ccff; color: #0b1e3b; font-weight: bold;
  padding: 12px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;
}
.submit-btn:disabled { background: #556; color: #888; }
.error-text { color: #ff6b6b; font-size: 0.9rem; }
.check-icon { font-size: 3rem; margin-bottom: 20px; }
</style>