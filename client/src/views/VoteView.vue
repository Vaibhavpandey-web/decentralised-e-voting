<script setup>
import { ref, watch, computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import FaceAuth from "../components/FaceAuth.vue";
import Icon from "../components/AppIcon.vue";
import {
  wallet,
  election,
  loadElection,
  readContract,
  writeContract,
  connectWallet,
  errorMessage,
  shortAddress,
  phases,
} from "../lib/chain";
const permit = ref(null),
  selected = ref(null),
  review = ref(false),
  busy = ref(false),
  message = ref(""),
  receipt = ref(null),
  eligibility = ref(null),
  eligibilityError = ref("");
const chosen = computed(() =>
  election.candidates.find((c) => c.id === selected.value)
);
let eligibilityRequest = 0;
async function checkEligibility() {
  const request = ++eligibilityRequest;
  eligibility.value = null;
  eligibilityError.value = "";
  if (!wallet.address || !election.loaded) return;
  try {
    const c = readContract();
    const [eligible, voted] = await Promise.all([
      c.eligible(wallet.address),
      c.hasVoted(wallet.address),
    ]);
    if (request === eligibilityRequest) eligibility.value = { eligible, voted };
  } catch (e) {
    if (request === eligibilityRequest)
      eligibilityError.value = errorMessage(e);
  }
}
watch(
  () => wallet.address,
  () => {
    permit.value = null;
    selected.value = null;
    review.value = false;
    receipt.value = null;
    message.value = "";
    checkEligibility();
  }
);
watch(() => election.loaded, checkEligibility);
onMounted(async () => {
  await loadElection();
  await checkEligibility();
});
async function vote() {
  busy.value = true;
  message.value = "";
  try {
    if (!permit.value || Date.now() / 1000 >= permit.value.deadline) {
      permit.value = null;
      review.value = false;
      throw Error("Verification expired. Please verify your identity again.");
    }
    const c = await writeContract();
    const address = await c.runner.getAddress();
    if (address.toLowerCase() !== permit.value.wallet.toLowerCase())
      throw Error("Wallet changed. Verify again before voting.");
    message.value =
      "Confirm the transaction in your wallet. This choice cannot be changed.";
    const tx = await c.vote(
      selected.value,
      permit.value.identity,
      permit.value.deadline,
      permit.value.signature
    );
    message.value =
      "Transaction submitted. Waiting for blockchain confirmation…";
    const result = await tx.wait();
    if (result.status !== 1)
      throw Error("The transaction reverted. Your vote was not recorded.");
    receipt.value = { hash: result.hash, block: result.blockNumber };
    permit.value = null;
    await loadElection();
  } catch (e) {
    message.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">YOUR VOICE / YOUR CHOICE</div>
      <h1>Make your vote count.</h1>
      <p>A considered choice. A verifiable record.</p>
    </div>
    <span class="tag"><Icon name="vote" />Voting booth</span>
  </div>
  <div class="progress-steps">
    <span :class="{ current: !permit && !receipt }">01 · Verify identity</span
    ><span :class="{ current: permit && !review }">02 · Choose a candidate</span
    ><span :class="{ current: review || receipt }"
      >03 · Confirm your ballot</span
    >
  </div>
  <section v-if="receipt" class="panel receipt">
    <div class="receipt-icon"><Icon name="check" /></div>
    <div class="eyebrow">CONFIRMED ON-CHAIN</div>
    <h1>Your voice is on record.</h1>
    <p>
      Your ballot was confirmed in block {{ receipt.block }}.<br />Keep the
      transaction hash to verify the record.
    </p>
    <code class="hash">{{ receipt.hash }}</code
    ><RouterLink class="button primary" to="/"
      >Return to overview<Icon name="arrow"
    /></RouterLink>
  </section>
  <div v-else class="split-layout">
    <section class="panel">
      <div v-if="!election.loaded" class="empty-state">
        <Icon name="globe" />
        <h2>Election unavailable</h2>
        <p>{{ election.error || "Connecting to the election…" }}</p>
        <button
          class="button"
          @click="loadElection"
          :disabled="election.loading"
        >
          Retry connection
        </button>
      </div>
      <div v-else-if="election.phase !== 1" class="empty-state">
        <Icon name="clock" />
        <h2>{{ phases[election.phase] }}</h2>
        <p>
          {{
            election.phase === 0
              ? "Voting begins when your administrator opens the election."
              : "This election has ended. View the recorded results on the overview."
          }}
        </p>
        <RouterLink to="/" class="button">View election</RouterLink>
      </div>
      <div v-else-if="!wallet.address" class="empty-state">
        <Icon name="wallet" />
        <h2>Connect your registered wallet</h2>
        <p>Use the wallet approved by your election administrator.</p>
        <button
          class="button primary"
          @click="connectWallet"
          :disabled="wallet.busy"
        >
          Connect wallet
        </button>
      </div>
      <div v-else-if="!eligibility" class="empty-state">
        <p>{{ eligibilityError || "Checking wallet eligibility…" }}</p>
        <button
          v-if="eligibilityError"
          class="button"
          @click="checkEligibility"
        >
          Try again
        </button>
      </div>
      <div
        v-else-if="!eligibility.eligible || eligibility.voted"
        class="empty-state"
      >
        <Icon name="shield" />
        <h2>
          {{
            eligibility.voted
              ? "You’ve already voted"
              : "Wallet approval needed"
          }}
        </h2>
        <p>
          {{
            eligibility.voted
              ? "Only one ballot is accepted per registered wallet and verified identity."
              : "Ask your administrator to approve this wallet before voting."
          }}
        </p>
      </div>
      <FaceAuth v-else-if="!permit" @verification-passed="permit = $event" />
      <div v-else-if="!review">
        <div class="eyebrow">IDENTITY VERIFIED</div>
        <h2>Choose your representative</h2>
        <p class="muted mt">
          Select one candidate. You’ll review your choice before signing.
        </p>
        <fieldset style="border: 0; padding: 0; margin: 0">
          <legend class="sr-only">Candidates</legend>
          <div class="candidate-grid">
            <label
              v-for="c in election.candidates"
              :key="c.id"
              :class="['candidate', { selected: selected === c.id }]"
              ><span class="avatar">{{ String(c.id).padStart(2, "0") }}</span
              ><span
                ><h3>{{ c.name }}</h3>
                <small>Candidate {{ c.id }}</small></span
              ><input
                v-model="selected"
                type="radio"
                name="candidate"
                :value="c.id"
            /></label>
          </div>
        </fieldset>
        <button
          class="button primary"
          :disabled="!selected"
          @click="review = true"
        >
          Review ballot<Icon name="arrow" />
        </button>
      </div>
      <div v-else>
        <div class="eyebrow">ONE LAST LOOK</div>
        <h2>Confirm your choice</h2>
        <div class="candidate selected mt">
          <span class="avatar">{{ selected }}</span>
          <h3>{{ chosen?.name }}</h3>
        </div>
        <div class="notice warning">
          A confirmed vote cannot be changed. Your wallet and candidate choice
          are publicly visible on-chain.
        </div>
        <div class="hero-actions">
          <button class="button primary" :disabled="busy" @click="vote">
            {{ busy ? "Processing…" : "Sign & cast vote" }}</button
          ><button class="button" :disabled="busy" @click="review = false">
            Change choice
          </button>
        </div>
      </div>
      <div v-if="message" class="notice" role="status">{{ message }}</div>
    </section>
    <aside class="panel" style="align-self: start">
      <h2>Your voting session</h2>
      <div class="row-line">
        <span>Wallet</span><strong>{{ shortAddress(wallet.address) }}</strong>
      </div>
      <div class="row-line">
        <span>Identity</span
        ><strong>{{ permit ? "Verified" : "Not verified" }}</strong>
      </div>
      <div class="row-line">
        <span>Ballot</span
        ><strong>{{ selected ? "Selected" : "Not selected" }}</strong>
      </div>
      <div class="info-note">
        <Icon name="shield" /><span
          >Your verification expires after five minutes. A ballot is only
          recorded after the transaction confirms.</span
        >
      </div>
      <p class="muted mt">
        You’ll need test ETH for network fees on a test network. This is an
        academic voting prototype.
      </p>
    </aside>
  </div>
</template>
