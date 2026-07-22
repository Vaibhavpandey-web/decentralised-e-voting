<template>
  <div>
    <!-- PHASE 1: Face Authentication Component -->
    <FaceAuth 
      v-if="!isVerified" 
      @verification-passed="handleSuccess" 
    />

    <!-- PHASE 2: The Blockchain Voting Booth -->
    <div v-else class="modern-overlay">
      <div class="glass-panel vote-panel">
        
        <div class="header-section" v-if="!receiptData">
          <h4 class="institute-title">Secure Voting Booth</h4>
          <h2 class="title">Cast Your Ballot</h2>
          <p class="subtitle">Verified Voter: <span class="highlight-roll">{{ verifiedRollNumber }}</span></p>
        </div>

        <!-- Ballot Selection -->
        <div v-if="!receiptData" class="ballot-container">
          <div class="input-wrapper">
            <label>Select Your Candidate</label>
            <select v-model="selectedCandidate" :disabled="isProcessing" class="modern-input">
              <option value="" disabled>-- Choose a Candidate --</option>
              <option value="1">Narendra Modi (BJP)</option>
              <option value="2">Rahul Gandhi (INC)</option>
              <option value="3">NOTA</option>
            </select>
          </div>

          <button @click="executeBlockchainVote" :disabled="isProcessing || !selectedCandidate" class="primary-btn vote-btn">
            {{ isProcessing ? 'Writing to Blockchain...' : 'Sign & Cast Vote' }}
          </button>
        </div>

        <!-- Digital Proof of Vote Receipt -->
        <div v-if="receiptData" class="receipt-card">
          <h3>✅ Official Voter Receipt</h3>
          <div class="receipt-details">
            <p><strong>Voter Roll No:</strong> <span class="highlight">{{ receiptData.rollNumber }}</span></p>
            <p><strong>Voted For:</strong> <span class="highlight-candidate">{{ receiptData.candidateName }}</span></p>
            <p><strong>Signing Address:</strong> <span class="signer-addr">{{ receiptData.signerAddress }}</span></p>
            <p><strong>Status:</strong> Immutably Recorded on Blockchain</p>
            <p><strong>Cryptographic Proof (Tx Hash):</strong></p>
            <p class="tx-hash">{{ receiptData.txHash }}</p>
          </div>
          <button @click="returnToHome" class="primary-btn close-btn-receipt">End Session</button>
        </div>

        <div v-if="statusMessage && !receiptData" :class="['status-message', statusType]">
          {{ statusMessage }}
        </div>

        <div class="footer-credits">
          <p>Decentralised E-Voting Engine Powered by Ethers.js</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import FaceAuth from '../components/FaceAuth.vue';
import { ethers } from "ethers";

// Replace with your latest compiled deployment address if you redeployed your contract
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"; 
const CONTRACT_ABI = [
  "function vote(uint256 candidateId) public",
  "function hasVoted(address voter) public view returns (bool)"
];

export default {
  name: "VoteView",
  components: {
    FaceAuth
  },
  data() {
    return {
      isVerified: false,
      verifiedRollNumber: null,
      selectedCandidate: "",
      isProcessing: false,
      statusMessage: "",
      statusType: "info",
      receiptData: null
    };
  },
  methods: {
    handleSuccess(rollNo) {
      this.verifiedRollNumber = rollNo;
      this.isVerified = true; 
    },
    
   async executeBlockchainVote() {
      this.isProcessing = true;
      this.statusMessage = "";
      
      try {
        // FIX 1: Removed ".providers" to match Ethers v6 syntax
        const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
        
        let signer = null;
        let activeAccountIndex = -1;

        this.setStatus("Scanning network for an eligible node address...", "info");

        for (let i = 0; i < 20; i++) {
          // FIX 2: Added "await" because getSigner is asynchronous in v6
          const tempSigner = await provider.getSigner(i);
          const tempAddress = await tempSigner.getAddress();
          const checkContract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, tempSigner);
          
          const alreadyVoted = await checkContract.hasVoted(tempAddress);
          
          if (!alreadyVoted) {
            signer = tempSigner;
            activeAccountIndex = i;
            break; 
          }
        }

        if (!signer) {
          this.setStatus("All 20 local test accounts have been exhausted. Please restart your Hardhat Node terminal.", "error");
          this.isProcessing = false;
          return;
        }

        const signerAddress = await signer.getAddress();
        const votingContract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

        const candidateNameString = 
          this.selectedCandidate === "1" ? "Narendra Modi (BJP)" : 
          this.selectedCandidate === "2" ? "Rahul Gandhi (INC)" : "NOTA";

        this.setStatus(`Signing via proxy ledger Account #${activeAccountIndex}...`, "info");
        
        const tx = await votingContract.vote(parseInt(this.selectedCandidate));
        this.setStatus(`Mining transaction block... Please wait.`, "info");
        
        const receipt = await tx.wait();

        if (receipt.status === 1) {
          // Sync with the Python backend ledger
          await fetch("http://localhost:5000/mark_voted", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ roll_no: this.verifiedRollNumber })
          });
          
          this.receiptData = {
            rollNumber: this.verifiedRollNumber,
            candidateName: candidateNameString,
            signerAddress: `${signerAddress.substring(0, 6)}...${signerAddress.substring(38)}`,
            // FIX 3: Ethers v6 uses receipt.hash, v5 used receipt.transactionHash. 
            // We use a fallback to guarantee the receipt prints!
            txHash: receipt.hash || receipt.transactionHash 
          };
        } else {
          this.setStatus("EVM Reverted the vote transaction execution.", "error");
        }
      } catch (error) {
        console.error(error);
        const userFriendlyError = error.reason || error.message || "Unknown Blockchain Error";
        this.setStatus(`Blockchain Error: ${userFriendlyError.substring(0, 60)}...`, "error");
      } finally {
        this.isProcessing = false;
      }
    },
    returnToHome() {
      this.isVerified = false;
      this.verifiedRollNumber = null;
      this.selectedCandidate = "";
      this.receiptData = null;
      this.statusMessage = "";
      this.$router.push('/');
    },

    setStatus(message, type) {
      this.statusMessage = message;
      this.statusType = type;
    }
  }
};
</script>

<style scoped>
.modern-overlay { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #0e1424, #202843, #2c3764); padding: 20px; }
.glass-panel { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 40px; width: 100%; max-width: 480px; box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); color: #fff; text-align: center; }
.header-section { margin-bottom: 25px; }
.institute-title { margin: 0 0 10px 0; color: #a0aec0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.title { margin: 0; font-size: 24px; font-weight: 600; }
.subtitle { margin: 10px 0 0 0; font-size: 15px; color: #cbd5e0; }
.highlight-roll { color: #00e676; font-weight: bold; font-size: 18px; background: rgba(0, 230, 118, 0.1); padding: 2px 8px; border-radius: 4px; }

.ballot-container { margin-top: 20px; }
.input-wrapper { text-align: left; margin-bottom: 25px; }
.input-wrapper label { display: block; font-size: 13px; color: #cbd5e0; margin-bottom: 8px; text-transform: uppercase; }
.modern-input { width: 100%; padding: 14px; background: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; color: #fff; font-size: 16px; outline: none; transition: all 0.3s ease; box-sizing: border-box; }
.modern-input option { color: #000; }

.primary-btn { width: 100%; padding: 15px; border: none; border-radius: 10px; color: white; font-size: 16px; font-weight: bold; cursor: pointer; transition: transform 0.2s ease; }
.vote-btn { background: linear-gradient(135deg, #1e3c72, #2a5298); }
.vote-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(30, 60, 114, 0.4); }
.primary-btn:disabled { background: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.3); cursor: not-allowed; }

.status-message { margin-top: 20px; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 500; }
.info { background: rgba(33, 150, 243, 0.2); color: #64b5f6; border: 1px solid #1976d2; }
.success { background: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid #388e3c; }
.error { background: rgba(244, 67, 54, 0.2); color: #e57373; border: 1px solid #d32f2f; }

/* Digital Receipt Styling */
.receipt-card { margin-top: 10px; background: rgba(255, 255, 255, 0.95); border-left: 6px solid #4CAF50; border-radius: 8px; padding: 25px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3); text-align: left; animation: slideDown 0.5s ease-out; color: #2c3e50; }
.receipt-card h3 { margin-top: 0; color: #2e7d32; border-bottom: 2px dashed #ccc; padding-bottom: 10px; }
.receipt-details p { margin: 12px 0; font-size: 14px; }
.highlight { font-size: 17px; font-weight: bold; color: #1976d2; }
.highlight-candidate { font-size: 16px; font-weight: 900; color: #d32f2f; background-color: #ffebee; padding: 2px 6px; border-radius: 4px; }
.signer-addr { font-family: monospace; font-size: 13px; background: #eceff1; padding: 2px 4px; border-radius: 4px; }
.tx-hash { background: #e0e0e0; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; word-break: break-all; color: #555; border: 1px solid #ccc; }
.close-btn-receipt { margin-top: 20px; background: #607d8b; }

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>