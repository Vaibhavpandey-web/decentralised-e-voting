<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<template>
  <div class="app-wrapper">
    <!-- Top Glassmorphism Navigation Bar -->
    <nav class="navbar glass-panel">
      <div class="nav-brand">
        <span class="logo">🗳️</span>
        <span class="brand-text">Secure E-Voting</span>
      </div>
      
      <div class="nav-links">
        <RouterLink to="/" class="nav-link">Home</RouterLink>
        <RouterLink to="/register" class="nav-link">Register Face</RouterLink>
        
        <!-- Admin Links -->
        <RouterLink to="/admin-dashboard" class="nav-link" style="color: #fca5a5;">Admin Dashboard</RouterLink>
        
        <!-- Voter Action -->
        <RouterLink to="/vote" class="nav-link btn-gradient">Cast Vote</RouterLink>
      </div>
    </nav>

    <!-- The RouterView acts as a window displaying your separate pages -->
    <main class="page-content">
      <RouterView /> 
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* GLOBAL VARIABLES */
:root {
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --border-color: rgba(255, 255, 255, 0.1);
  --primary: #6366f1;
  --secondary: #3b82f6;
}

/* MASTER BACKGROUND & TYPOGRAPHY */
html, body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
  
  /* 🟢 The Animated Deep-Space Gradient */
  background: linear-gradient(-45deg, #0f172a, #1e1b4b, #1e293b, #0c4a6e);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  background-attachment: fixed;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.app-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

/* NAVIGATION BAR STYLING */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  margin-bottom: 40px;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.2s, transform 0.2s;
}

.nav-link:hover {
  color: var(--text-main);
}

/* Highlights the active page the user is currently on */
.router-link-active:not(.btn-gradient) {
  color: #60a5fa;
  font-weight: 600;
}

/* SPECIAL GRADIENT BUTTON FOR VOTING */
.btn-gradient {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  padding: 10px 24px;
  border-radius: 8px;
  color: white !important;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
}

/* SMOOTH PAGE TRANSITIONS */
.page-content {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* MOBILE RESPONSIVENESS */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
  }
  .nav-links {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>