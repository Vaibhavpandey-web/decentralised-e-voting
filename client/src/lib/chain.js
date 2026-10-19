import { reactive } from "vue";
import {
  BrowserProvider,
  Contract,
  JsonRpcProvider,
  FetchRequest,
  isAddress,
} from "ethers";
import artifact from "../Voting.json";
export const config = {
  address: import.meta.env.VITE_CONTRACT_ADDRESS || "",
  chainId: Number(import.meta.env.VITE_CHAIN_ID || 31337),
  rpc: import.meta.env.VITE_RPC_URL || "http://127.0.0.1:8545",
  api: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000",
};
export const wallet = reactive({ address: "", error: "", busy: false });
export const election = reactive({
  loaded: false,
  loading: false,
  error: "",
  title: "Campus Council Election",
  phase: null,
  total: 0,
  registered: 0,
  candidates: [],
  admin: "",
});
export const phases = ["Registration open", "Voting open", "Election closed"];
export const shortAddress = (v) =>
  v ? `${v.slice(0, 6)}…${v.slice(-4)}` : "Not connected";
export function errorMessage(e) {
  return e.code === 4001 || e.code === "ACTION_REJECTED"
    ? "Request cancelled in your wallet. You can try again."
    : e.reason || e.shortMessage || e.message || "Please try again.";
}
function ensureConfig() {
  if (!isAddress(config.address))
    throw Error(
      "Election not connected. Configure the deployed contract address to begin."
    );
}
let readProvider;
export function readContract() {
  ensureConfig();
  if (!readProvider) {
    const req = new FetchRequest(config.rpc);
    req.timeout = 10000;
    readProvider = new JsonRpcProvider(req, config.chainId);
  }
  return new Contract(config.address, artifact.abi, readProvider);
}
export async function signer() {
  if (!window.ethereum)
    throw Error("Install an Ethereum wallet such as MetaMask to continue.");
  const p = new BrowserProvider(window.ethereum);
  if (Number((await p.getNetwork()).chainId) !== config.chainId)
    throw Error(
      `Switch your wallet to chain ${config.chainId}, then reconnect.`
    );
  const s = await p.getSigner();
  wallet.address = await s.getAddress();
  return s;
}
export async function connectWallet() {
  wallet.busy = true;
  wallet.error = "";
  try {
    if (!window.ethereum)
      throw Error("Install an Ethereum wallet such as MetaMask to continue.");
    await window.ethereum.request({ method: "eth_requestAccounts" });
    await signer();
  } catch (e) {
    wallet.error = errorMessage(e);
  } finally {
    wallet.busy = false;
  }
}
export async function writeContract() {
  ensureConfig();
  return new Contract(config.address, artifact.abi, await signer());
}
export async function loadElection() {
  if (election.loading) return;
  election.loading = true;
  election.error = "";
  try {
    const c = readContract();
    const [title, phase, total, registered, count, admin] = await Promise.all([
      c.title(),
      c.phase(),
      c.totalVotes(),
      c.registeredCount(),
      c.candidatesCount(),
      c.admin(),
    ]);
    const candidates = await Promise.all(
      Array.from({ length: Number(count) }, async (_, i) => {
        const r = await c.candidates(i + 1);
        return { id: Number(r.id), name: r.name, votes: Number(r.voteCount) };
      })
    );
    Object.assign(election, {
      title,
      phase: Number(phase),
      total: Number(total),
      registered: Number(registered),
      candidates,
      admin,
      loaded: true,
    });
  } catch (e) {
    election.loaded = false;
    election.error = errorMessage(e);
  } finally {
    election.loading = false;
  }
}
export async function api(path, body, token) {
  const r = await fetch(config.api + path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(60000),
  });
  const d = await r.json();
  if (!r.ok) throw Error(d.message || "Verification service unavailable.");
  return d;
}
if (typeof window !== "undefined" && window.ethereum?.on) {
  for (const event of ["accountsChanged", "chainChanged"])
    window.ethereum.on(event, () => {
      wallet.address = "";
      wallet.error = "Wallet or network changed. Reconnect to continue.";
    });
}
