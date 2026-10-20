<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";
import Icon from "../components/AppIcon.vue";
import {
  election,
  phases,
  loadElection,
  config,
  shortAddress,
} from "../lib/chain";
const metrics = computed(() => [
  {
    label: "Registered voters",
    value: election.registered,
    note: "Approved wallets",
    icon: "user",
  },
  {
    label: "Ballots recorded",
    value: election.total,
    note: "Confirmed on-chain",
    icon: "vote",
  },
  {
    label: "Voter turnout",
    value:
      (election.registered
        ? Math.round((election.total / election.registered) * 100)
        : 0) + "%",
    note: "Of registered wallets",
    icon: "chart",
  },
  {
    label: "Candidates",
    value: election.candidates.length,
    note: "On this election’s ballot",
    icon: "grid",
  },
]);
const steps = [
  [
    "Register your identity",
    "Enroll with your election administrator and have your wallet approved.",
  ],
  [
    "Verify it’s you",
    "Connect your wallet and complete a quick camera verification.",
  ],
  [
    "Cast it. Confirm it.",
    "Review your choice, sign the transaction and keep your confirmation.",
  ],
];
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">EVERY VOICE MATTERS</div>
      <h1>Your vote. Our future.</h1>
      <p>A clear view of your election, from registration to results.</p>
    </div>
    <span class="tag"><Icon name="shield" />Transparent by design</span>
  </div>
  <section class="hero">
    <div class="hero-copy">
      <div class="eyebrow">PARTICIPATION STARTS WITH YOU</div>
      <h2>Small action.<br /><em>Lasting impact.</em></h2>
      <p>
        Take part in your community’s next chapter. Verify your identity, choose
        your candidate and make your voice count.
      </p>
      <div class="hero-actions">
        <RouterLink class="button lime" to="/vote"
          >Enter voting booth<Icon name="arrow" /></RouterLink
        ><RouterLink class="text-link" to="/register"
          >Get registered<Icon name="arrow"
        /></RouterLink>
      </div>
    </div>
    <div class="hero-art" aria-hidden="true">
      <div class="orbit"></div>
      <div class="orbit two"></div>
      <div class="orbit three"></div>
      <div class="ballot-box">
        <div class="ballot-paper"><Icon name="check" /></div>
        <Icon name="vote" />
      </div>
      <span class="art-label"><Icon name="check" />A voice that counts.</span>
    </div>
  </section>
  <div class="metric-grid">
    <article v-for="m in metrics" :key="m.label" class="metric">
      <div class="metric-label">{{ m.label }}<Icon :name="m.icon" /></div>
      <strong>{{ election.loaded ? m.value : "—" }}</strong
      ><small>{{
        election.loaded ? m.note : "Awaiting election connection"
      }}</small>
    </article>
  </div>
  <div class="overview-grid">
    <section class="panel">
      <div class="section-heading">
        <div>
          <h2>A simple path to participation</h2>
          <p>Three steps. One meaningful choice.</p>
        </div>
        <Icon name="arrow" />
      </div>
      <div class="steps">
        <div v-for="(s, i) in steps" :key="i" class="step">
          <span class="step-number">0{{ i + 1 }}</span>
          <div>
            <h3>{{ s[0] }}</h3>
            <p>{{ s[1] }}</p>
          </div>
        </div>
      </div>
    </section>
    <section class="panel">
      <div class="section-heading">
        <h2>Election at a glance</h2>
        <button
          class="button ghost"
          @click="loadElection"
          :disabled="election.loading"
          aria-label="Refresh election"
        >
          <Icon name="refresh" />
        </button>
      </div>
      <div class="row-line">
        <span>Election</span><strong>{{ election.title }}</strong>
      </div>
      <div class="row-line">
        <span>Current phase</span
        ><strong>{{
          election.loaded ? phases[election.phase] : "Not connected"
        }}</strong>
      </div>
      <div class="row-line">
        <span>Network</span
        ><strong>{{
          config.chainId === 31337
            ? "Local Ethereum"
            : `Chain ${config.chainId}`
        }}</strong>
      </div>
      <div class="row-line">
        <span>Contract</span
        ><strong>{{
          config.address ? shortAddress(config.address) : "Not configured"
        }}</strong>
      </div>
      <div class="info-note">
        <Icon name="globe" /><span
          >This prototype uses a public ledger. Wallets and vote choices are
          visible on-chain.</span
        >
      </div>
    </section>
  </div>
  <div v-if="election.error" class="notice warning" role="status">
    {{ election.error }}
    <button
      class="button ghost"
      @click="loadElection"
      :disabled="election.loading"
    >
      Retry connection
    </button>
  </div>
  <section
    v-if="election.loaded && election.candidates.length"
    class="panel mt"
  >
    <div class="section-heading">
      <div>
        <h2>
          {{ election.phase === 2 ? "Election results" : "On the ballot" }}
        </h2>
        <p>Candidate information read directly from your election contract.</p>
      </div>
      <span class="tag">{{ election.candidates.length }} candidates</span>
    </div>
    <div v-for="c in election.candidates" :key="c.id" class="results-row">
      <div class="result-label">
        <strong>{{ c.name }}</strong
        ><span>{{
          election.phase === 2
            ? `${c.votes} votes`
            : `Candidate ${String(c.id).padStart(2, "0")}`
        }}</span>
      </div>
      <div v-if="election.phase === 2" class="bar">
        <span
          :style="{
            width:
              (election.total ? (c.votes / election.total) * 100 : 0) + '%',
          }"
        ></span>
      </div>
    </div>
  </section>
</template>
