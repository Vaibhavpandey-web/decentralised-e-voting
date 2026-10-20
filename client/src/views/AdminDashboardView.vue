<script setup>
import { ref, computed, onMounted } from "vue";
import Icon from "../components/AppIcon.vue";
import {
  election,
  wallet,
  connectWallet,
  loadElection,
  writeContract,
  errorMessage,
  phases,
} from "../lib/chain";
const name = ref(""),
  address = ref(""),
  busy = ref(false),
  message = ref(""),
  failed = ref(false),
  confirmPhase = ref(""),
  editingId = ref(null),
  editingName = ref("");
const isAdmin = computed(
  () =>
    wallet.address &&
    wallet.address.toLowerCase() === election.admin.toLowerCase()
);
onMounted(loadElection);
async function run(method, ...args) {
  busy.value = true;
  failed.value = false;
  message.value = "Approve the transaction in your administrator wallet.";
  try {
    const c = await writeContract();
    const tx = await c[method](...args);
    message.value = "Waiting for on-chain confirmation…";
    await tx.wait();
    message.value = "Change confirmed on-chain.";
    name.value = "";
    address.value = "";
    confirmPhase.value = "";
    editingId.value = null;
    await loadElection();
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
      <div class="eyebrow">ELECTION OPERATIONS</div>
      <h1>A clear view. Full control.</h1>
      <p>Manage candidates, approve wallets and move your election forward.</p>
    </div>
    <button class="button" @click="loadElection" :disabled="election.loading">
      <Icon name="refresh" />Refresh
    </button>
  </div>
  <div v-if="!election.loaded" class="notice warning">
    {{ election.error || "Connecting to the election…" }}
  </div>
  <section v-else-if="!isAdmin" class="panel empty-state">
    <Icon name="shield" />
    <h2>Administrator wallet required</h2>
    <p>
      Connect the wallet that deployed this election.<br />Permissions are
      enforced by the smart contract.
    </p>
    <button
      class="button primary"
      @click="connectWallet"
      :disabled="wallet.busy"
    >
      Connect administrator wallet
    </button>
    <div v-if="wallet.address" class="notice warning">
      The connected wallet is not this election’s administrator.
    </div>
  </section>
  <div v-else>
    <div v-if="message" :class="['notice', { error: failed }]" role="status">
      {{ message }}
    </div>
    <div class="metric-grid">
      <article class="metric">
        <div class="metric-label">Election phase<Icon name="clock" /></div>
        <h3>{{ phases[election.phase] }}</h3>
        <small>Only forward transitions</small>
      </article>
      <article class="metric">
        <div class="metric-label">Approved wallets<Icon name="user" /></div>
        <strong>{{ election.registered }}</strong>
      </article>
      <article class="metric">
        <div class="metric-label">Recorded ballots<Icon name="vote" /></div>
        <strong>{{ election.total }}</strong>
      </article>
      <article class="metric">
        <div class="metric-label">Candidates<Icon name="grid" /></div>
        <strong>{{ election.candidates.length }}</strong>
      </article>
    </div>
    <div class="admin-grid">
      <section class="panel">
        <h2>Candidate management</h2>
        <form
          v-if="election.phase === 0"
          class="inline-form"
          @submit.prevent="run('addCandidate', name.trim())"
        >
          <label class="field"
            >Candidate name<input
              v-model="name"
              required
              maxlength="100"
              placeholder="e.g. Ananya Sharma"
              :disabled="busy" /></label
          ><button class="button primary" :disabled="busy || !name.trim()">
            Add candidate
          </button>
        </form>
        <div v-if="!election.candidates.length" class="empty-state mt">
          <p>Add at least two candidates before opening voting.</p>
        </div>
        <div v-for="c in election.candidates" :key="c.id" class="results-row">
          <div class="result-label">
            <strong>{{ c.name }}</strong
            ><button
              v-if="election.phase === 0 && editingId !== c.id"
              class="button ghost"
              :disabled="busy"
              @click="
                editingId = c.id;
                editingName = c.name;
              "
            >
              Edit name</button
            ><span>{{ c.votes }} votes</span>
          </div>
          <form
            v-if="editingId === c.id"
            class="inline-form mt"
            @submit.prevent="
              run('updateCandidateName', c.id, editingName.trim())
            "
          >
            <label class="field"
              >New candidate name<input
                v-model="editingName"
                required
                maxlength="100"
                :disabled="busy" /></label
            ><button class="button" :disabled="busy || !editingName.trim()">
              Save</button
            ><button
              type="button"
              class="button ghost"
              :disabled="busy"
              @click="editingId = null"
            >
              Cancel
            </button>
          </form>
          <div class="bar">
            <span
              :style="{
                width:
                  (election.total ? (c.votes / election.total) * 100 : 0) + '%',
              }"
            ></span>
          </div>
        </div>
        <p v-if="election.phase !== 0" class="muted mt">
          Candidate details are locked after registration closes.
        </p>
      </section>
      <section class="panel">
        <h2>Approve a voter wallet</h2>
        <form
          v-if="election.phase === 0"
          class="form-stack"
          @submit.prevent="run('registerVoter', address.trim())"
        >
          <p class="muted">
            Check the voter’s identity and biometric enrollment first, then
            approve their exact wallet address.
          </p>
          <label class="field"
            >Wallet address<input
              v-model="address"
              required
              pattern="0x[a-fA-F0-9]{40}"
              placeholder="0x…"
              :disabled="busy" /></label
          ><button class="button primary" :disabled="busy">
            Approve on-chain
          </button>
        </form>
        <p v-else class="muted">
          Voter registration is closed for this election.
        </p>
        <div class="info-note">
          <Icon name="shield" /><span
            >Approval allows this wallet to participate. Casting a vote also
            requires a valid biometric verification signature.</span
          >
        </div>
      </section>
      <section class="panel">
        <h2>Election lifecycle</h2>
        <p class="muted">
          {{
            election.phase === 0
              ? "Opening voting locks candidate details and the voter list."
              : election.phase === 1
              ? "Closing voting permanently ends ballot submission."
              : "This election is closed. Results and voter history remain on-chain."
          }}
        </p>
        <template v-if="election.phase < 2"
          ><button
            v-if="!confirmPhase"
            class="button mt"
            :disabled="
              busy ||
              (election.phase === 0 &&
                (election.candidates.length < 2 || !election.registered))
            "
            @click="confirmPhase = election.phase === 0 ? 'open' : 'close'"
          >
            {{ election.phase === 0 ? "Open voting" : "Close voting" }}
          </button>
          <div v-else class="notice warning">
            <p>
              This transition cannot be undone.
              {{
                confirmPhase === "open"
                  ? "Confirm the candidate and voter lists are complete."
                  : "Confirm you are ready to end voting."
              }}
            </p>
            <div class="hero-actions">
              <button
                class="button primary"
                :disabled="busy"
                @click="
                  run(confirmPhase === 'open' ? 'openVoting' : 'closeVoting')
                "
              >
                Confirm {{ confirmPhase }}</button
              ><button
                class="button"
                :disabled="busy"
                @click="confirmPhase = ''"
              >
                Cancel
              </button>
            </div>
          </div></template
        >
      </section>
      <section class="panel">
        <h2>Preserve the record</h2>
        <p class="muted">
          This dashboard cannot erase ballots or reset identity history. Deploy
          a new contract for a new election.
        </p>
        <div class="info-note">
          <Icon name="globe" /><span
            >Vote choices and totals are public on-chain, including while voting
            is open. This system does not provide secret ballots.</span
          >
        </div>
      </section>
    </div>
  </div>
</template>
