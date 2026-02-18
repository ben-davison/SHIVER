<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import { useRouter } from 'vue-router';

const router = useRouter();
const profile = ref(null);
const loading = ref(true);

// Helper to format date
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};

// Helper to format usage type for display
const formatType = (type) => {
  const map = {
    'cube_download': 'Data Cube',
    'chart_export': 'Chart Image',
    'data_download': 'Timeseries',
    'map_click': 'Map Click'
  };
  return map[type] || type || 'Download';
};

// Fetch Data
onMounted(async () => {
  try {
    const token = sessionStorage.getItem('shiver_token'); // Ensure you are saving the token!
    if (!token) throw new Error("No token");

    const res = await apiClient.get('/api/users/me', {
       headers: { Authorization: `Bearer ${token}` }
    });
    profile.value = res.data;
  } catch (error) {
    console.error(error);
    router.push('/'); // Redirect if not auth
  } finally {
    loading.value = false;
  }
});

const logout = () => {
  sessionStorage.removeItem('shiver_auth');
  sessionStorage.removeItem('shiver_token');
  window.location.href = "/"; // Hard reload to clear state
};
</script>

<template>
  <div class="profile-container">
    <div class="profile-card" v-if="profile">
      
      <div class="profile-header">
        <div class="avatar-circle">{{ profile.email[0].toUpperCase() }}</div>
        <h2>My Account</h2>
        <p class="email-text">{{ profile.email }}</p>
      </div>

      <div class="stats-grid">
        <div class="stat-box highlight">
          <span class="stat-val">{{ profile.total_volume_mb.toFixed(1) }} MB</span>
          <span class="stat-label">Total Data Extracted</span>
        </div>

        <div class="stat-box">
          <span class="stat-val">{{ profile.usage_breakdown.cube_download || 0 }}</span>
          <span class="stat-label">Data Cubes</span>
        </div>

        <div class="stat-box">
          <span class="stat-val">{{ profile.usage_breakdown.chart_export || 0 }}</span>
          <span class="stat-label">Charts Created</span>
        </div>

        <div class="stat-box">
          <span class="stat-val">{{ profile.usage_breakdown.data_download || 0 }}</span>
          <span class="stat-label">Timeseries Batches</span>
        </div>
		
		<div class="stat-box">
          <span class="stat-val">{{ profile.usage_breakdown.map_click || 0 }}</span>
          <span class="stat-label">Timeseries visualisations</span>
        </div>
      </div>

      <div class="history-section">
        <h3>Recent Activity</h3>
        <div class="history-list">
          <div v-for="(item, index) in profile.recent_downloads" :key="index" class="history-item">
            <div class="file-info">
              <span class="file-name">{{ item.filename }}</span>
              <span class="file-date">{{ formatDate(item.date) }}</span>
            </div>
            <div class="file-meta">
              <span class="file-type-badge" :class="item.type">{{ formatType(item.type) }}</span>
              <span class="file-size">{{ item.size ? item.size.toFixed(2) + ' MB' : '< 0.1 MB' }}</span>
            </div>
          </div>
          <p v-if="profile.recent_downloads.length === 0" class="no-data">No recent activity.</p>
        </div>
      </div>

      <button class="logout-btn" @click="logout">Log Out</button>
    </div>

    <div v-else-if="loading" class="loading-state">Loading Profile...</div>
  </div>
</template>

<style scoped>
.profile-container {
  display: flex; justify-content: center; padding-top: 50px;
  background: #f4f7f9; min-height: 100vh;
}

.profile-card {
  background: white; width: 100%; max-width: 600px;
  border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  padding: 40px; text-align: center; height: fit-content;
}

.profile-header { margin-bottom: 30px; }
.avatar-circle {
  width: 80px; height: 80px; background: #0b1e3b; color: #00ccff;
  font-size: 2.5rem; font-weight: bold; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 15px auto;
}
.email-text { color: #666; font-size: 1.1rem; }

/* STATS GRID */
.stats-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 15px;
  margin-bottom: 40px;
}

.stat-box {
  background: #f8f9fa; padding: 20px; border-radius: 8px;
  border: 1px solid #eee; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.stat-box.highlight { background: #e6f7ff; border-color: #b3e0ff; }
.stat-box.highlight .stat-val { color: #0088cc; }

.stat-val { font-size: 1.8rem; font-weight: 800; color: #0b1e3b; line-height: 1.2; }
.stat-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 5px; }

/* HISTORY LIST */
.history-section { text-align: left; margin-bottom: 30px; }
.history-section h3 { font-size: 1.1rem; color: #0b1e3b; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }

.history-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0; border-bottom: 1px solid #f0f0f0;
}
.history-item:last-child { border-bottom: none; }

.file-info { display: flex; flex-direction: column; }
.file-name { font-weight: 600; color: #333; font-size: 0.95rem; }
.file-date { font-size: 0.8rem; color: #999; margin-top: 2px; }

.file-meta { text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.file-size { font-size: 0.85rem; color: #666; font-family: monospace; }

/* BADGES */
.file-type-badge {
  font-size: 0.7rem; padding: 2px 8px; border-radius: 12px;
  font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;
}
.file-type-badge.cube_download { background: #e3f2fd; color: #1565c0; } /* Blue */
.file-type-badge.chart_export { background: #e8f5e9; color: #2e7d32; } /* Green */
.file-type-badge.data_download { background: #fff3e0; color: #ef6c00; } /* Orange */

.logout-btn {
  background: white; border: 1px solid #ff4d4d; color: #ff4d4d;
  padding: 10px 25px; border-radius: 20px; cursor: pointer;
  font-weight: 600; transition: all 0.2s;
}
.logout-btn:hover { background: #ff4d4d; color: white; }
</style>