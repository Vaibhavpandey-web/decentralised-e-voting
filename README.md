# Decentralised E-Voting

A proof-of-concept decentralised e-voting application that combines:
- a Solidity smart contract for on-chain vote recording (contracts/Voting.sol),
- a Python backend that handles voter verification (server/app.py, server/image.py) and stores lightweight server-side state (server/admins.json, server/voted.json),
- a Vue + Vite frontend (client/) with a face-authentication UI component (client/src/components/FaceAuth.vue).

This repository demonstrates how on-chain voting can be integrated with an off-chain voter authentication flow (face-based) and a simple web UI.

---

## Quick highlights
- Smart contract: contracts/Voting.sol (Solidity ^0.8.0) — simple candidate registry + one-vote-per-address enforcement.
- Backend: server/app.py — Python Flask-style HTTP backend and image processing (server/image.py). The repository includes the dlib face predictor binary: server/shape_predictor_68_face_landmarks.dat.
- Frontend: client/ — Vue single-file components (App.vue, FaceAuth.vue) served with Vite.

---

## Stack
- Languages: Solidity, JavaScript/Node.js, Python, HTML/CSS
- Framework / runtime:
  - Smart contract: Hardhat (development & deployment tooling)
  - Frontend: Vue.js + Vite
  - Backend: Python (Flask or simple WSGI app; see server/app.py)
- Notable libraries & tools:
  - Solidity ^0.8.0 (contracts/Voting.sol)
  - Hardhat (hardhat.config.js)
  - Vite (client/vite.config.js)
  - dlib / face-landmark model (server/shape_predictor_68_face_landmarks.dat)
  - Typical Python imaging libs likely required: OpenCV / dlib / numpy (see server/ files)

---

## Repository layout
```
client/                      # Vue + Vite frontend
  index.html
  package.json
  vite.config.js
  src/
    App.vue                  # main app view
    main.js
    style.css
    components/
      FaceAuth.vue           # face authentication UI
      HelloWorld.vue
    router/
      index.js
    Voting.json              # local voting data used by the frontend
server/                      # Python backend + face auth support
  app.py                     # backend API server
  image.py                   # image processing / face auth helpers
  admins.json                # admin configuration
  voted.json                 # simple store for votes (server-side)
  shape_predictor_68_face_landmarks.dat  # dlib model (~99 MB)
contracts/                   # smart contract(s)
  Voting.sol                 # on-chain voting contract
hardhat.config.js            # Hardhat configuration
Gemini_Generated_Image_.png  # repository image asset
.artifacts/ .venv/ .vscode/  # local/dev artifacts & editor configs
```

How it fits together:
- Frontend (client/src) handles UI and user flow, including capturing/collecting face images for authentication (FaceAuth.vue).
- Backend (server/app.py) receives authentication images, runs face processing (image.py + dlib model) and responds with allow/deny decisions; it also keeps a small JSON-based record of which addresses/users have voted (server/voted.json).
- Smart contract (contracts/Voting.sol) is deployed to a local or test Ethereum network via Hardhat; votes are recorded on-chain by calling the contract's `vote(candidateId)` function from the wallet/address that is allowed to vote.

---

## How to run (development)

Prerequisites
- Node.js (recommended v16+)
- npm
- Python 3.8+
- pip
- (Optional) A local Ethereum node or Hardhat Network (Hardhat provides an in-memory node)

1) Clone
```bash
git clone https://github.com/Vaibhavpandey-web/decentralised-e-voting.git
cd decentralised-e-voting
```

2) Run the smart-contract environment (Hardhat)
- Ensure Node & npm are installed. From the repo root:
```bash
# install hardhat locally (if you don't already have package.json in root)
npm init -y
npm install --save-dev hardhat
# add other dev deps as needed, for example: @nomiclabs/hardhat-ethers ethers
# then compile
npx hardhat compile
# (optional) run a local node
npx hardhat node
```
- Deploy the contract using your Hardhat scripts or manually using a console/ethers — you will need to adapt or add a deploy script.

Note: contracts/Voting.sol currently seeds three sample candidates in the constructor:
- "Narendra Modi (BJP)"
- "Rahul Gandhi (INC)"
- "NOTA"

The contract prevents an address from voting more than once using the `hasVoted` mapping.

3) Start the backend (Python)
- Create and activate a virtual environment, install dependencies:
```bash
cd server
python3 -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Install dependencies (adjust as needed; there is no requirements.txt in the repo)
pip install flask numpy opencv-python dlib
```
- Start the server:
```bash
python app.py
```
- The server includes the dlib shape predictor binary at server/shape_predictor_68_face_landmarks.dat. This file is large (~99 MB) and is required for the face-landmark based operations.

4) Start the frontend (Vue + Vite)
```bash
cd client
npm install
npm run dev
# or
npx vite
```
- Open the dev server address shown by Vite (usually http://localhost:5173).

5) Wire things together
- Configure the frontend to talk to your backend endpoint (the client code references a local API URL in the components; edit client/src as needed).
- Configure the contract address & provider in whichever script or frontend module you use to call the contract. Typical env vars:
  - WEB3_PROVIDER_URL (e.g., http://localhost:8545 or Hardhat node RPC)
  - CONTRACT_ADDRESS
  - PRIVATE_KEY (for deployments — keep secret)

---

## Notes & caveats
- This repository is a proof-of-concept — it is not production ready. In particular:
  - The server uses JSON files (server/voted.json, server/admins.json) for state — replace with a proper DB for real deployments.
  - Face-based authentication here is illustrative; biometric authentication carries strong privacy, security, and regulatory requirements. Do not use this code as-is for real elections.
  - The smart contract includes a very simple vote mechanism and a `hasVoted` mapping; think carefully about identity, vote privacy, and replay protections before production use.
- The dlib predictor binary (server/shape_predictor_68_face_landmarks.dat) is included in the repo; consider large-file storage (LFS) or downloading the model during setup instead of committing it.
- There is no top-level README in the repository (this file fills that gap). There is no license file — add one if you intend to publish the code.

---

## Development tips
- If you add deployment scripts for the contract, put them in a `scripts/` folder and document the Hardhat commands here.
- Add a `requirements.txt` in `server/` to capture Python dependencies for reproducible setup.
- Add a root `package.json` if you intend to run Hardhat from the repo root; otherwise document per-directory setup explicitly.

---

## Contributing
Contributions, bug reports and improvements are welcome. When opening a PR, please:
- Explain the change and its purpose.
- Keep cryptographic/secret keys out of the repo (use .env or secrets).
- Add tests for new contract logic and for any backend features.

---

## License
No license file present in the repository. If you want others to reuse this project, add a LICENSE (for example, MIT) to the repo.

---

## Useful places to look in this repo
- contracts/Voting.sol — the on-chain voting contract
- server/app.py, server/image.py — backend and face processing
- server/shape_predictor_68_face_landmarks.dat — dlib landmark model (required by server)
- client/src/ — frontend UI and FaceAuth.vue component
- hardhat.config.js — Hardhat configuration for smart contract development

```
