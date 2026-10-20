<script setup>
import { ref } from "vue";
import Camera from "../components/CameraCapture.vue";
import Icon from "../components/AppIcon.vue";
import { api, errorMessage } from "../lib/chain";
const camera = ref(),
  roll = ref(""),
  address = ref(""),
  token = ref(""),
  consent = ref(false),
  busy = ref(false),
  message = ref(""),
  failed = ref(false);
async function enroll() {
  busy.value = true;
  message.value = "";
  failed.value = false;
  try {
    if (!consent.value)
      throw Error("Consent is required to enroll biometrics.");
    await api(
      "/register",
      {
        roll_no: roll.value.trim(),
        wallet: address.value.trim(),
        image: camera.value.capture(),
        consent: true,
      },
      token.value
    );
    message.value =
      "Identity enrolled. Your administrator must also approve this wallet on-chain before voting opens.";
    token.value = "";
    camera.value.stop();
  } catch (e) {
    failed.value = true;
    message.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">STEP 01 / GET READY</div>
      <h1>Make it official.</h1>
      <p>Register your identity with your election administrator.</p>
    </div>
    <span class="tag"><Icon name="user" />Supervised enrollment</span>
  </div>
  <div class="split-layout">
    <section class="panel">
      <form class="form-stack" @submit.prevent="enroll">
        <Camera ref="camera" /><label class="field"
          >Voter ID / roll number<input
            v-model="roll"
            required
            pattern="[A-Za-z0-9_-]{1,40}"
            maxlength="40"
            placeholder="e.g. CSE2026001"
            :disabled="busy"
            autocomplete="off"
          /><small>Use the ID issued by your institution.</small></label
        ><label class="field"
          >Voter wallet address<input
            v-model="address"
            required
            pattern="0x[a-fA-F0-9]{40}"
            placeholder="0x…"
            :disabled="busy"
            spellcheck="false"
          /><small
            >This wallet will sign your ballot. Use your own wallet
            address.</small
          ></label
        ><label class="field"
          >Administrator enrollment token<input
            v-model="token"
            type="password"
            required
            placeholder="Entered by your administrator"
            :disabled="busy"
            autocomplete="off" /></label
        ><label class="check-label"
          ><input
            v-model="consent"
            type="checkbox"
            required
            :disabled="busy"
          />I consent to storing a face encoding for this demonstration
          election. I understand the administrator controls this biometric
          record.</label
        ><button class="button primary" :disabled="busy || !consent">
          {{ busy ? "Enrolling identity…" : "Capture & enroll identity"
          }}<Icon name="arrow" />
        </button>
        <div
          v-if="message"
          :class="['notice', { error: failed }]"
          role="status"
        >
          {{ message }}
        </div>
      </form>
    </section>
    <aside class="panel" style="align-self: start">
      <h2>Before you begin</h2>
      <div class="steps">
        <div class="step">
          <span class="step-number">01</span>
          <div>
            <h3>Bring your voter ID</h3>
            <p>Your administrator checks eligibility before enrollment.</p>
          </div>
        </div>
        <div class="step">
          <span class="step-number">02</span>
          <div>
            <h3>Use one personal wallet</h3>
            <p>
              One voter ID is bound to one wallet. Existing records cannot be
              overwritten here.
            </p>
          </div>
        </div>
        <div class="step">
          <span class="step-number">03</span>
          <div>
            <h3>Complete wallet approval</h3>
            <p>
              Biometric enrollment and on-chain approval are separate steps.
              Your administrator completes both.
            </p>
          </div>
        </div>
      </div>
      <div class="info-note">
        <Icon name="shield" /><span
          >Face encodings stay on the verification server. They are never
          written to the blockchain.</span
        >
      </div>
    </aside>
  </div>
</template>
