<script setup>
import { ref } from 'vue';
import { BrowserProvider, ContractFactory, isAddress } from 'ethers';
import deployment from '../VotingDeployment.json';
import { errorMessage } from '../lib/chain';
const title = ref('Campus Council Election');
const verifier = import.meta.env.VITE_VERIFIER_ADDRESS || '';
const busy = ref(false), message = ref(''), address = ref(''), transaction = ref('');
async function deploy() {
  busy.value = true;
  message.value = '';
  try {
    if (!window.ethereum) throw Error('Open this page in MetaMask’s browser, or install its browser extension.');
    if (!isAddress(verifier)) throw Error('The verification signer has not been configured.');
    if (!title.value.trim() || title.value.trim().length > 100) throw Error('Enter an election title of 1–100 characters.');
    await window.ethereum.request({ method: 'eth_requestAccounts' });
    await window.ethereum.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: '0xaa36a7' }] });
    const provider = new BrowserProvider(window.ethereum);
    if ((await provider.getNetwork()).chainId !== 11155111n) throw Error('Switch to Sepolia testnet to continue.');
    const signer = await provider.getSigner();
    message.value = 'Review the contract deployment in your wallet. It uses Sepolia test ETH.';
    const contract = await new ContractFactory(deployment.abi, deployment.bytecode, signer).deploy(title.value.trim(), verifier);
    transaction.value = contract.deploymentTransaction().hash;
    message.value = 'Transaction submitted. Waiting for confirmation…';
    await contract.waitForDeployment();
    address.value = await contract.getAddress();
    message.value = 'Contract deployed. Share the public contract address below to finish connecting the backend and frontend.';
  } catch (error) {
    message.value = errorMessage(error);
  } finally { busy.value = false; }
}
</script>
<template>
  <div class="page-heading"><div><div class="eyebrow">ONE-TIME SETUP · SEPOLIA</div><h1>Connect your election.</h1><p>Deploy the contract from a test wallet you control.</p></div></div>
  <section class="setup-panel">
    <h2>Before you deploy</h2>
    <p>Your connected wallet becomes the election administrator. Use a dedicated test wallet with Sepolia test ETH. No real ETH is needed.</p>
    <p>Only deploy once. If you already deployed this election, share its public contract address instead.</p>
    <label for="election-title">Election title</label>
    <input id="election-title" v-model="title" maxlength="100" :disabled="busy || !!address" />
    <p>Verification signer: <code>{{ verifier || 'Not configured' }}</code></p>
    <button class="button" @click="deploy" :disabled="busy || !!address || !verifier">{{ busy ? 'Waiting for your wallet…' : address ? 'Contract deployed' : 'Deploy on Sepolia' }}</button>
    <p role="status" aria-live="polite">{{ message }}</p>
    <p v-if="transaction"><a :href="`https://sepolia.etherscan.io/tx/${transaction}`" target="_blank" rel="noopener noreferrer">View deployment transaction</a></p>
    <p v-if="address">Contract address: <code>{{ address }}</code></p>
    <p class="muted">Deployment creates an empty election. Candidate setup, voter enrollment and wallet approval happen after the services are connected.</p>
  </section>
</template>
<style scoped>
.setup-panel{max-width:760px;padding:32px;border:1px solid #d9dfd4;border-radius:24px;background:#fffdf7}.setup-panel p{line-height:1.65;margin:18px 0}.setup-panel label{display:block;margin:22px 0 8px;font-weight:600}.setup-panel input{width:100%;padding:14px;border:1px solid #ccd5ca;border-radius:10px;font:inherit;box-sizing:border-box}.setup-panel code{overflow-wrap:anywhere}.muted{color:#667369;font-size:.9rem}
</style>
