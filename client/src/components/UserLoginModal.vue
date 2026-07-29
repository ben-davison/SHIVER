<script setup>
import { ref, watch } from 'vue';
import axios from 'axios'; 
import { API_URL } from '../api'; 

// 1. Accept the reset token from App.vue
const props = defineProps({
  resetToken: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['close', 'login-success']);

// Form Inputs
const email = ref('');
const password = ref('');
const confirmPassword = ref(''); // For registration

// UI States
// viewMode can be: 'login', 'register', 'reset'
const viewMode = ref('login'); 
const isLoading = ref(false);
const errorMsg = ref('');
const successMsg = ref('');
const showPassword = ref(false);

// 2. Watch for the token prop. If it exists, immediately switch to the confirm-reset view.
watch(() => props.resetToken, (newToken) => {
  if (newToken) {
    switchMode('confirm-reset');
  }
}, { immediate: true });

// --- HELPER: RESET STATE WHEN SWITCHING MODES ---
const switchMode = (mode) => {
  viewMode.value = mode;
  errorMsg.value = '';
  successMsg.value = '';
  password.value = '';
  confirmPassword.value = '';
};

// --- ACTION 1: LOGIN ---
const handleLogin = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  
  try {
    const payload = { email: email.value, password: password.value };
    const response = await axios.post(`${API_URL}/auth/login`, payload);

    sessionStorage.setItem('shiver_token', response.data.access_token);
    emit('login-success');
    emit('close'); 

  } catch (err) {
    if (err.response && (err.response.status === 400 || err.response.status === 429)) {
        // Dynamically display the exact detail string we sent from FastAPI
        errorMsg.value = err.response.data.detail;
    } else {
        // Fallback for 500 server errors or actual lost connections
        errorMsg.value = "Login failed. Please check your connection.";
    }
  } finally {
    isLoading.value = false;
  }
};

// --- ACTION 2: REGISTER ---
const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    errorMsg.value = "Passwords do not match.";
    return;
  }
  
  isLoading.value = true;
  errorMsg.value = '';

  try {
    const payload = { email: email.value, password: password.value };
    // Call the register endpoint
    const response = await axios.post(`${API_URL}/auth/register`, payload);
    
    // Registration usually returns a token (auto-login), so we save it immediately
    sessionStorage.setItem('shiver_token', response.data.access_token);
    
    emit('login-success');
    emit('close');

  } catch (err) {
    console.error(err);
    if (err.response && err.response.data.detail) {
       errorMsg.value = err.response.data.detail; // e.g., "Email already registered"
    } else {
       errorMsg.value = "Registration failed. Please try again.";
    }
  } finally {
    isLoading.value = false;
  }
};

// --- ACTION 3: PASSWORD RESET REQUEST ---
const handleResetRequest = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  successMsg.value = '';

  try {
    await axios.post(`${API_URL}/auth/request-password-reset`, { email: email.value });
    successMsg.value = "If an account exists, a reset link has been sent.";
  } catch (err) {
    errorMsg.value = "Could not send reset email.";
  } finally {
    isLoading.value = false;
  }
};


// --- ACTION 4: CONFIRM PASSWORD RESET ---
const handlePasswordResetConfirm = async () => {
  if (password.value !== confirmPassword.value) {
    errorMsg.value = "Passwords do not match.";
    return;
  }
  
  isLoading.value = true;
  errorMsg.value = '';
  successMsg.value = '';

  try {
    const payload = { 
      token: props.resetToken, 
      new_password: password.value 
    };
    await axios.post(`${API_URL}/auth/reset-password`, payload);
    
    // Switch back to login view and show success
    switchMode('login');
    successMsg.value = "Password updated successfully! Please log in with your new password.";
    
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
        errorMsg.value = err.response.data.detail; 
    } else {
        errorMsg.value = "Failed to reset password. The link may have expired.";
    }
  } finally {
    isLoading.value = false;
  }
};


const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

// --- PREVENT ACCIDENTAL CLOSURE ---
let clickStartedOnBackdrop = false;

const handleMouseDown = (e) => {
  // We only care if the click started on the backdrop itself, not the card
  clickStartedOnBackdrop = e.target.classList.contains('modal-backdrop');
};

const handleMouseUp = (e) => {
  // Only close if the click started ON the backdrop AND ended ON the backdrop
  if (clickStartedOnBackdrop && e.target.classList.contains('modal-backdrop')) {
    emit('close');
  }
  // Reset for the next interaction
  clickStartedOnBackdrop = false;
};


</script>

<template>
  <div 
    class="modal-backdrop" 
    @mousedown="handleMouseDown" 
    @mouseup="handleMouseUp"
  >
    <div class="modal-card" @mousedown.stop @mouseup.stop> 
      <button class="close-btn" @click="$emit('close')">x</button>
      
      <h2 v-if="viewMode === 'login'">User Login</h2>
      <h2 v-else-if="viewMode === 'register'">Create Account</h2>
	  <h2 v-else-if="viewMode === 'confirm-reset'">Create New Password</h2>
      <h2 v-else>Reset Password</h2>
      
      <p class="subtext" v-if="viewMode === 'login'">Login to access all SHIVER functions.</p>
      <p class="subtext" v-else-if="viewMode === 'register' || viewMode === 'confirm-reset'">
         <strong>Note:</strong> Passwords must be at least 10 characters long, contain at least one letter, at least one number and at least one special character.
      </p>
      <p class="subtext" v-else>Enter your email to receive a password reset link.</p>

      <div v-if="successMsg" class="success-banner">{{ successMsg }}</div>

      <form @submit.prevent="
			viewMode === 'login' ? handleLogin() : 
			viewMode === 'register' ? handleRegister() : 
			viewMode === 'confirm-reset' ? handlePasswordResetConfirm() :
			handleResetRequest()
      " class="login-form">
        
        <div v-if="viewMode !== 'confirm-reset'">
          <label>Email</label>
          <input type="email" v-model="email" required placeholder="name@example.com" class="dark-input">
        </div>
        
        <div v-if="viewMode !== 'reset'">
            <label>Password</label>
            <div class="password-wrapper">
                <input 
                    :type="showPassword ? 'text' : 'password'" 
                    v-model="password" 
                    required 
                    placeholder="********" 
                    class="dark-input password-input"
                    minlength="10"
                >
                <button type="button" class="eye-btn" @click="togglePasswordVisibility" tabindex="-1">
                    <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                </button>
            </div>
            
            <div class="forgot-link-wrapper" v-if="viewMode === 'login'">
                <a href="#" class="link-text" @click.prevent="switchMode('reset')">Forgot Password?</a>
            </div>
        </div>

        <div v-if="viewMode === 'register' || viewMode === 'confirm-reset'">
            <label>Confirm Password</label>
            <input 
                type="password" 
                v-model="confirmPassword" 
                required 
                placeholder="********" 
                class="dark-input"
            >
        </div>

        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading">Processing...</span>
          <span v-else-if="viewMode === 'login'">Log In</span>
          <span v-else-if="viewMode === 'register'">Create Account</span>
          <span v-else-if="viewMode === 'confirm-reset'">Update Password</span>
          <span v-else>Send Reset Link</span>
        </button>

        <div class="modal-footer">
            <div v-if="viewMode === 'login'">
                Don't have an account? 
                <a href="#" class="link-text bold" @click.prevent="switchMode('register')">Register</a>
            </div>

            <div v-if="viewMode === 'register'">
                Already have an account? 
                <a href="#" class="link-text bold" @click.prevent="switchMode('login')">Log In</a>
            </div>

            <button v-if="viewMode === 'reset' || viewMode === 'confirm-reset'" type="button" class="back-btn" @click="switchMode('login')">
                Back to Log In
            </button>
        </div>

      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6);
  z-index: 3000;
  display: flex; justify-content: center; align-items: center;
  user-select: none;
}
.modal-card {
  background: #1a2634; color: white;
  padding: 30px; border-radius: 8px; width: 100%; max-width: 400px;
  position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  user-select: auto;
}
.close-btn {
  position: absolute; top: 10px; right: 15px;
  background: none; border: none; color: #888; font-size: 1.5rem; cursor: pointer;
}
.subtext { color: #8fa1b3; margin-bottom: 20px; font-size: 0.9rem; }
.login-form { display: flex; flex-direction: column; gap: 15px; }

/* INPUTS */
.dark-input {
  background: #0b1e3b; border: 1px solid #2c3e50;
  color: white; padding: 10px; border-radius: 4px; width: 100%;
  box-sizing: border-box; 
}
.dark-input:focus { border-color: #00ccff; outline: none; }

/* PASSWORD EYE */
.password-wrapper { position: relative; width: 100%; }
.password-input { padding-right: 40px; } 
.eye-btn {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 0;
}

/* LINKS */
.forgot-link-wrapper { text-align: right; margin-top: 5px; }
.link-text { color: #00ccff; font-size: 0.9rem; text-decoration: none; }
.link-text:hover { text-decoration: underline; }
.link-text.bold { font-weight: bold; }

/* BUTTONS */
.submit-btn {
  background: #00ccff; color: #0b1e3b; font-weight: bold;
  padding: 12px; border: none; border-radius: 4px; cursor: pointer; margin-top: 5px;
}
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.back-btn {
  background: transparent; color: #8fa1b3; border: 1px solid #2c3e50;
  padding: 8px; border-radius: 4px; cursor: pointer; width: 100%;
}
.back-btn:hover { color: white; border-color: #8fa1b3; }

/* FOOTER */
.modal-footer { margin-top: 15px; text-align: center; font-size: 0.9rem; color: #8fa1b3; }

.error-text { color: #ff6b6b; font-size: 0.9rem; margin: 0; }
.success-banner {
    background: rgba(46, 204, 113, 0.2); border: 1px solid #2ecc71;
    color: #2ecc71; padding: 10px; border-radius: 4px; font-size: 0.9rem; margin-bottom: 10px;
}
</style>