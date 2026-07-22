<template>
  <div class="modern-overlay">
    <div class="glass-panel">
      <div class="header-section">
        <h2 class="title">Voter Registration</h2>
        <p class="subtitle">Enroll biometrics into the Decentralised System</p>
      </div>
      
      <div class="video-container">
        <video ref="videoElement" autoplay playsinline></video>
        <canvas ref="canvasElement" width="640" height="480" style="display: none;"></canvas>
      </div>

      <div class="input-wrapper">
        <label for="rollNo">Assign Roll Number</label>
        <input 
          type="number" 
          id="rollNo" 
          v-model="rollNumber" 
          placeholder="Enter a unique ID"
          :disabled="isProcessing"
          class="modern-input"
        />
      </div>

      <button @click="registerVoter" :disabled="isProcessing || !rollNumber" class="primary-btn">
        {{ isProcessing ? 'Encoding Face...' : 'Capture & Register' }}
      </button>

      <div v-if="statusMessage" :class="['status-message', statusType]">
        {{ statusMessage }}
      </div>

     
    </div>
  </div>
</template>

<script>
export default {
  name: "RegisterView",
  data() {
    return {
      rollNumber: "",
      isProcessing: false,
      statusMessage: "",
      statusType: "info",
    };
  },
  mounted() {
    this.startCamera();
  },
  beforeUnmount() {
    this.stopCamera();
  },
  methods: {
    async startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        if (this.$refs.videoElement) {
          this.$refs.videoElement.srcObject = stream;
        }
      } catch (error) {
        this.setStatus("Camera access denied.", "error");
      }
    },
    stopCamera() {
      if (this.$refs.videoElement && this.$refs.videoElement.srcObject) {
        const tracks = this.$refs.videoElement.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
    },
    async registerVoter() {
      this.isProcessing = true;
      this.statusMessage = "";
      
      const canvas = this.$refs.canvasElement;
      const video = this.$refs.videoElement;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const singleFrameB64 = canvas.toDataURL('image/jpeg');

      this.setStatus("Sending data to AI Engine...", "info");

      try {
        const response = await fetch("http://localhost:5000/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            roll_no: this.rollNumber,
            image: singleFrameB64
          })
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
          this.setStatus(`Success! Roll No ${this.rollNumber} is now registered.`, "success");
          this.rollNumber = ""; 
        } else {
          this.setStatus(result.message || "Failed to register.", "error");
        }
      } catch (error) {
        this.setStatus("Backend connection failed. Is app.py running?", "error");
      } finally {
        this.isProcessing = false;
      }
    },
    setStatus(message, type) {
      this.statusMessage = message;
      this.statusType = type;
    }
  }
};
</script>

<style scoped>
.modern-overlay { display: flex; justify-content: center; align-items: center; min-height: 100vh;  background: linear-gradient(135deg, #0e1424, #202843, #2c3764); padding: 20px; }
.glass-panel { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 40px; width: 100%; max-width: 480px; box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); color: #fff; text-align: center; }
.header-section { margin-bottom: 25px; }
.institute-title { margin: 0 0 10px 0; color: #a0aec0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.title { margin: 0; font-size: 24px; font-weight: 600; }
.subtitle { margin: 5px 0 0 0; font-size: 14px; color: #cbd5e0; }
.video-container { position: relative; width: 100%; border-radius: 12px; overflow: hidden; background: #000; border: 2px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
video { width: 100%; height: auto; display: block; }
.input-wrapper { text-align: left; margin-bottom: 25px; }
.input-wrapper label { display: block; font-size: 13px; color: #cbd5e0; margin-bottom: 8px; text-transform: uppercase; }
.modern-input { width: 100%; padding: 14px; background: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; color: #fff; font-size: 16px; outline: none; transition: all 0.3s ease; box-sizing: border-box; }
.modern-input:focus { border-color: #00e676; box-shadow: 0 0 0 3px rgba(0, 230, 118, 0.2); }
.primary-btn { width: 100%; padding: 15px; background: linear-gradient(135deg, #00b09b, #96c93d); border: none; border-radius: 10px; color: white; font-size: 16px; font-weight: bold; cursor: pointer; transition: transform 0.2s ease; }
.primary-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(150, 201, 61, 0.4); }
.primary-btn:disabled { background: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.3); cursor: not-allowed; }
.status-message { margin-top: 20px; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 500; }
.info { background: rgba(33, 150, 243, 0.2); color: #64b5f6; border: 1px solid #1976d2; }
.success { background: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid #388e3c; }
.error { background: rgba(244, 67, 54, 0.2); color: #e57373; border: 1px solid #d32f2f; }
.footer-credits { margin-top: 25px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 11px; color: #718096; }
</style>