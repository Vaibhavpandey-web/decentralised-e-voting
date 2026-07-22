<script setup>
import { ref, onMounted } from 'vue';
import { ethers } from 'ethers';
import VotingArtifact from '../Voting.json'; 

// ⚠️ PASTE YOUR NEW DEPLOYED CONTRACT ADDRESS HERE
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
const totalVotes = ref(0);
const notification = ref({ show: false, message: "", type: "success" });

const showNotification = (message, type = "success") => {
  notification.value = { show: true, message, type };
  setTimeout(() => { notification.value.show = false; }, 4000);
};

const loadStats = async () => {
  try {
     const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
     const contract = new ethers.Contract(CONTRACT_ADDRESS, VotingArtifact.abi, provider);
  
     const count = await contract.candidatesCount();
     let total = 0;

     // Dynamically sum votes from all candidates
     for(let i = 1; i <= Number(count); i++) {
       const c = await contract.candidates(i);
       total += Number(c.voteCount);
     }
     
     totalVotes.value = total;
  } catch (e) {
      console.error("Blockchain Error:", e);
      showNotification("Could not connect to the local blockchain.", "error");
  }
};

onMounted(loadStats);
</script>

<template>
  <div class="home-view">
    <transition name="slide-fade">
      <div v-if="notification.show" :class="['toast', `toast-${notification.type}`]">
        {{ notification.message }}
      </div>
    </transition>

    <header class="hero-panel glass">
      <div class="hero-content">
        <h1 class="title">Welcome to Next-Gen E-Voting</h1>
        <p class="subtitle">Experience the security of Biometric Verification combined with the immutability of Ethereum Smart Contracts.</p>
      </div>
      <div class="stats-box">
        <span class="stats-label">Live Votes Cast</span>
        <strong class="stats-value">{{ totalVotes }}</strong>
      </div>
    </header>
  </div>
</template>

<style scoped>
.glass {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}
.hero-panel { padding: 40px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; margin-top: 40px; }
.title { font-size: 2.2rem; margin: 0 0 10px 0; font-weight: 700; color: white; }
.subtitle { color: #94a3b8; font-size: 1.1rem; max-width: 500px; margin: 0; line-height: 1.5; }
.stats-box { background: rgba(0,0,0,0.3); padding: 20px 30px; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.3); display: flex; flex-direction: column; align-items: flex-end; }
.stats-label { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
.stats-value { font-size: 3rem; font-weight: 700; color: #60a5fa; line-height: 1; margin-top: 5px; }

.toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); padding: 12px 24px; border-radius: 8px; font-weight: 500; z-index: 1000; }
.toast-success { background: #064e3b; color: #34d399; border: 1px solid #047857; }
.toast-error { background: #7f1d1d; color: #fca5a5; border: 1px solid #b91c1c; }
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translate(-50%, -20px); }
</style>