<script setup>
import { ref } from 'vue';
import { ethers } from 'ethers';
import VotingArtifact from '../Voting.json'; 

const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

const candidates = ref([]);
const totalVotes = ref(0);
const isLoading = ref(false);
const notification = ref({ show: false, message: "", type: "success" });

// Admin Security State
const isUnlocked = ref(false);
const masterKeyInput = ref("");
const newCandidateName = ref("");

const showNotification = (message, type = "success") => {
  notification.value = { show: true, message, type };
  setTimeout(() => { notification.value.show = false; }, 4000);
};

const unlockDashboard = () => {
  if (masterKeyInput.value === "superadmin123") {
    isUnlocked.value = true;
    showNotification("Admin Dashboard Unlocked", "success");
    loadCandidates();
  } else {
    showNotification("Invalid Master Key", "error");
  }
};

const votePercent = (count) => {
  if (!totalVotes.value) return 0;
  return Math.round((count / totalVotes.value) * 100);
};

const loadCandidates = async () => {
  try {
     const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
     const contract = new ethers.Contract(CONTRACT_ADDRESS, VotingArtifact.abi, provider);
  
     const count = await contract.candidatesCount();
     let loadedCandidates = [];
     let total = 0;

     for(let i = 1; i <= Number(count); i++) {
       const c = await contract.candidates(i);
       const votes = Number(c.voteCount);
       total += votes;
       loadedCandidates.push({ id: i, name: c.name, voteCount: votes });
     }
     
     totalVotes.value = total;
     candidates.value = loadedCandidates;
  } catch (e) {
      showNotification("Could not connect to blockchain.", "error");
  }
};

const editCandidateName = async (id, currentName) => {
  const newName = prompt(`Enter new name for ${currentName}:`);
  if (!newName || newName === currentName) return;

  isLoading.value = true;
  try {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const signer = await provider.getSigner(0); 
    const contract = new ethers.Contract(CONTRACT_ADDRESS, VotingArtifact.abi, signer);

    const tx = await contract.updateCandidateName(id, newName);
    showNotification("Mining update on blockchain...", "success");
    await tx.wait(); 

    showNotification(`Candidate renamed to ${newName}`, "success");
    await loadCandidates(); 
  } catch (error) {
    showNotification("Smart Contract Error.", "error");
  } finally {
    isLoading.value = false;
  }
};

const addNewCandidate = async () => {
  if (!newCandidateName.value) return showNotification("Enter a candidate name.", "error");

  isLoading.value = true;
  try {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const signer = await provider.getSigner(0); 
    const contract = new ethers.Contract(CONTRACT_ADDRESS, VotingArtifact.abi, signer);

    const tx = await contract.addCandidate(newCandidateName.value);
    showNotification("Mining new candidate...", "success");
    await tx.wait(); 

    showNotification(`${newCandidateName.value} added!`, "success");
    newCandidateName.value = ""; 
    await loadCandidates(); 
  } catch (error) {
    showNotification("Smart Contract Error.", "error");
  } finally {
    isLoading.value = false;
  }
};

const resetElection = async () => {
  const username = prompt("Enter Admin Username to authorize wipe:");
  if (!username) return; 
  const password = prompt("Enter Admin Password to authorize wipe:");
  if (!password) return; 
  
  isLoading.value = true;
  try {
    // 1. Fixed URL & Domain to match Python Backend exactly
    const res = await fetch("http://localhost:5000/wipe_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }) 
    });
    
    const data = await res.json();
    
    // 2. Fixed the condition to look for 'status' instead of 'success'
    if (res.ok && data.status === "success") {
      showNotification("Off-chain Biometrics & Ledgers Wiped!", "success");

      // 3. Safety Wrapper for the Blockchain Reset
      try {
        const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
        const signer = await provider.getSigner(0);
        const contract = new ethers.Contract(CONTRACT_ADDRESS, VotingArtifact.abi, signer);
        
        // Checks if the contract actually supports an on-chain reset
        if (typeof contract.resetElection === 'function') {
          const tx = await contract.resetElection();
          await tx.wait(); 
          showNotification("Blockchain Election completely reset!", "success");
        } else {
          // If the function doesn't exist, it gracefully warns you instead of crashing
          showNotification("Note: Redeploy your Hardhat node to wipe on-chain votes.", "info");
        }
      } catch (bcError) {
        console.warn("Blockchain reset skipped:", bcError);
      }

      await loadCandidates(); 
    } else {
      showNotification(data.message || "Backend rejected wipe command.", "error"); 
    }
  } catch (e) { 
    console.error(e);
    // Makes the error more descriptive so you know if Python is offline
    showNotification("Network Error: Is the Python API running?", "error"); 
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="admin-dashboard">
    <transition name="slide-fade">
      <div v-if="notification.show" :class="['toast', `toast-${notification.type}`]">
        {{ notification.message }}
      </div>
    </transition>

    <!-- LOCKED STATE -->
    <div v-if="!isUnlocked" class="lock-screen glass">
      <h2>🔒 Restricted Access</h2>
      <p>Enter the System Master Key to access the live election dashboard.</p>
      <input v-model="masterKeyInput" type="password" placeholder="Enter Master Key" @keyup.enter="unlockDashboard"/>
      <button class="btn-primary" @click="unlockDashboard">Unlock Dashboard</button>
    </div>

    <!-- UNLOCKED STATE -->
    <div v-else class="dashboard-content">
      <header class="admin-header glass">
        <div>
          <h2>⚙️ Live Election Control Center</h2>
          <p>Total Votes Cast: <strong>{{ totalVotes }}</strong></p>
        </div>
        <button class="btn-danger" @click="resetElection" :disabled="isLoading">
          ⚠️ Wipe Election Data
        </button>
      </header>

      <div class="add-candidate-panel glass">
        <h3>Add New Candidate</h3>
        <div class="add-row">
          <input v-model="newCandidateName" placeholder="Candidate Name" :disabled="isLoading" />
          <button class="btn-success" @click="addNewCandidate" :disabled="isLoading">➕ Add to Blockchain</button>
        </div>
      </div>

      <div class="grid">
        <div v-for="c in candidates" :key="c.id" class="admin-card glass">
          <div class="card-head">
            <h3>{{ c.name }}</h3>
            <button class="btn-edit" @click="editCandidateName(c.id, c.name)">✏️ Edit Name</button>
          </div>
          <div class="vote-stats">
            <span class="vote-count">{{ c.voteCount }} Votes</span>
            <span class="percent">{{ votePercent(c.voteCount) }}%</span>
          </div>
          <div class="progress"><div class="bar" :style="{ width: votePercent(c.voteCount) + '%' }"></div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.glass { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; }
.lock-screen { max-width: 400px; margin: 60px auto; text-align: center; display: flex; flex-direction: column; gap: 16px; }
.lock-screen input { padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; text-align: center; font-size: 1.1rem; }
.btn-primary { background: #6366f1; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.admin-header h2 { margin: 0 0 8px 0; color: #60a5fa; }
.btn-danger { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.5); padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.btn-danger:hover { background: #ef4444; color: white; }
.add-candidate-panel { margin-bottom: 24px; }
.add-candidate-panel h3 { margin-top: 0; }
.add-row { display: flex; gap: 12px; }
.add-row input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; }
.btn-success { background: #10b981; color: white; border: none; padding: 0 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.admin-card { display: flex; flex-direction: column; gap: 16px; }
.card-head { display: flex; justify-content: space-between; align-items: center; }
.card-head h3 { margin: 0; font-size: 1.2rem; }
.btn-edit { background: transparent; border: 1px solid rgba(255,255,255,0.2); color: white; border-radius: 6px; padding: 6px 12px; cursor: pointer; }
.vote-stats { display: flex; justify-content: space-between; align-items: center; }
.vote-count { font-size: 1.5rem; font-weight: 700; color: #93c5fd; }
.percent { color: #94a3b8; font-weight: 600; }
.progress { height: 8px; background: rgba(255,255,255,0.1); border-radius: 999px; overflow: hidden; }
.bar { height: 100%; background: linear-gradient(90deg, #6366f1, #3b82f6); transition: width 1s ease; }
.toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); padding: 12px 24px; border-radius: 8px; font-weight: 500; z-index: 1000; }
.toast-success { background: #064e3b; color: #34d399; border: 1px solid #047857; }
.toast-error { background: #7f1d1d; color: #fca5a5; border: 1px solid #b91c1c; }
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translate(-50%, -20px); }
</style>