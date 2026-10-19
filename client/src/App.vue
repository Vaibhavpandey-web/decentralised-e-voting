<script setup>
import { onMounted } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import Icon from "./components/AppIcon.vue";
import {
  wallet,
  connectWallet,
  shortAddress,
  election,
  loadElection,
  config,
} from "./lib/chain";
const route = useRoute();
const links = [
  { to: "/", label: "Overview", icon: "grid" },
  { to: "/register", label: "Voter registration", icon: "user" },
  { to: "/vote", label: "Cast your vote", icon: "vote" },
  { to: "/admin-dashboard", label: "Election admin", icon: "shield" },
];
onMounted(loadElection);
</script>
<template>
  <a class="skip-link" href="#main">Skip to content</a>
  <aside class="sidebar">
    <RouterLink to="/" class="brand"
      ><span class="brand-symbol"><Icon name="vote" /></span
      ><span
        >civic<span class="brand-dot">.</span
        ><small>DECENTRALISED E-VOTING</small></span
      ></RouterLink
    >
    <div class="nav-caption">YOUR ELECTION SPACE</div>
    <nav aria-label="Main navigation">
      <RouterLink
        v-for="item in links"
        :key="item.to"
        :to="item.to"
        :class="['nav-item', { active: route.path === item.to }]"
        ><Icon :name="item.icon" />{{ item.label
        }}<span v-if="route.path === item.to" class="nav-dot"></span
      ></RouterLink>
    </nav>
    <div class="sidebar-bottom">
      <div class="trust-icon"><Icon name="shield" /></div>
      <h4>Your voice. On record.</h4>
      <p>Every confirmed ballot leaves a verifiable on-chain record.</p>
      <span class="mini-label">BUILT ON ETHEREUM <Icon name="globe" /></span>
    </div>
    <div class="sidebar-foot">
      <span class="avatar small">VP</span
      ><span>Community election<small>Academic demonstration</small></span>
    </div>
  </aside>
  <div class="workspace">
    <header class="topbar">
      <div class="breadcrumb">
        Workspace <span>/</span
        ><strong>{{ links.find((l) => l.to === route.path)?.label }}</strong>
      </div>
      <div class="top-actions">
        <span class="network-pill"
          ><i :class="{ online: election.loaded }"></i
          >{{
            config.chainId === 31337
              ? "Local Ethereum"
              : `Chain ${config.chainId}`
          }}</span
        ><button
          class="button wallet-button"
          @click="connectWallet"
          :disabled="wallet.busy"
        >
          <Icon name="wallet" />{{
            wallet.busy
              ? "Connecting…"
              : wallet.address
              ? shortAddress(wallet.address)
              : "Connect wallet"
          }}
        </button>
      </div>
    </header>
    <main id="main">
      <div v-if="wallet.error" class="notice warning" role="alert">
        {{ wallet.error }}
      </div>
      <RouterView />
    </main>
    <footer class="main-footer">
      <span>Civic / A more transparent way to participate.</span
      ><span>Public ledger · Academic prototype</span>
    </footer>
  </div>
</template>
