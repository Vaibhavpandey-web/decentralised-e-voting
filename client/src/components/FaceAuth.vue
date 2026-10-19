<script setup>
import { ref, onBeforeUnmount } from "vue";
import Camera from "./CameraCapture.vue";
import { api, signer, wallet, errorMessage } from "../lib/chain";
const emit = defineEmits(["verification-passed"]);
const camera = ref(),
  roll = ref(""),
  busy = ref(false),
  message = ref(""),
  failed = ref(false);
let disposed = false;
onBeforeUnmount(() => (disposed = true));
async function verify() {
  busy.value = true;
  failed.value = false;
  try {
    const account = await signer();
    const address = await account.getAddress();
    const challenge = await api("/challenge", {
      roll_no: roll.value.trim(),
      wallet: address,
    });
    message.value = "Approve the identity verification message in your wallet.";
    const signature = await account.signMessage(challenge.message);
    message.value =
      "Look at the camera, then slowly turn your head in either direction.";
    await new Promise((r) => setTimeout(r, 1500));
    if (disposed) return;
    const frames = await camera.value.burst();
    message.value = "Checking identity and movement…";
    const result = await api("/verify", {
      nonce: challenge.nonce,
      signature,
      frames,
    });
    if (disposed) return;
    if (wallet.address.toLowerCase() !== address.toLowerCase())
      throw Error("Wallet changed. Verify again with the original wallet.");
    camera.value.stop();
    emit("verification-passed", { ...result, wallet: address });
  } catch (e) {
    failed.value = true;
    message.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <form class="form-stack" @submit.prevent="verify">
    <div>
      <h2>Verify your identity</h2>
      <p class="muted mt">
        Keep your face visible throughout the capture. You’ll sign a wallet
        message before the camera check.
      </p>
    </div>
    <Camera ref="camera" /><label class="field"
      >Registered voter ID<input
        v-model="roll"
        required
        pattern="[A-Za-z0-9_-]{1,40}"
        maxlength="40"
        placeholder="Your registered roll number"
        :disabled="busy"
    /></label>
    <div v-if="message" :class="['notice', { error: failed }]" role="status">
      {{ message }}
    </div>
    <button class="button primary" :disabled="busy || !wallet.address">
      {{ busy ? "Verifying…" : "Verify & continue" }}
    </button>
  </form>
</template>
