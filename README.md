# Civic · Decentralised E-Voting

Vue 3 election dashboard, Solidity voting contract and Flask biometric verification service. Redesigned around supervised registration, personal wallets and transaction receipts.

**Academic prototype only:** wallets and vote choices are public on-chain. Face matching/head movement is not production-grade liveness detection. This is not suitable for real public elections or secret ballots.

## Features

- Responsive ivory-and-emerald dashboard: election overview, enrollment, voting booth and administrator controls.
- Personal wallet signing using ethers v6; explicit chain checks and transaction confirmation.
- Admin-approved wallets; registration → voting → closed lifecycle.
- Five-minute biometric permits bound to chain, contract, wallet and secret-keyed identity digest; OpenZeppelin signature recovery.
- Duplicate-vote protection by wallet and identity, on-chain.
- Authenticated enrollment, SQLite uniqueness/transactions, one-use wallet challenges, request limits, explicit CORS origins.
- No public wipe/reset or client-controlled vote-ledger endpoints.

## Setup

Use Node.js 22.13+ (22 LTS recommended), Python 3.10–3.12, an Ethereum browser wallet and a webcam. `face-recognition` requires native dlib/CMake/C++ tooling. On Windows, use WSL2 for the Python service if native installation fails. Do not reuse the original repository's checked-in Windows virtual environment.

```bash
npm ci
npm --prefix client ci
python -m venv server/venv
source server/venv/bin/activate
# Windows PowerShell instead: .\server\venv\Scripts\Activate.ps1
python -m pip install -r server/requirements.txt
cp server/.env.example server/.env
cp client/.env.example client/.env
```

### Create the verification authority

Run locally and keep the output private:

```bash
python -c "from eth_account import Account; a=Account.create(); print('Address:', a.address); print('Private key:', a.key.hex())"
python -c "import secrets; print(secrets.token_hex(32)); print(secrets.token_hex(32))"
```

Set `VERIFIER_PRIVATE_KEY` to the generated key in `server/.env`. Set `ADMIN_TOKEN` and `IDENTITY_SECRET` to the two independent random secrets. Save the verifier address for deployment. This account only signs permits and needs no test ETH. Never put secrets in frontend `VITE_*` variables or commit completed `.env` files. Keep the identity secret unchanged for the lifetime of an election.

### Start a local chain

Terminal A:

```bash
npm run node
```

Terminal B, replace with the verifier address:

```bash
VERIFIER_ADDRESS=0xYourVerificationSignerAddress npm run deploy:local
# PowerShell: $env:VERIFIER_ADDRESS='0xYourVerificationSignerAddress'; npm run deploy:local
```

Deployment generates the client ABI and prints the contract address. Copy it into `CONTRACT_ADDRESS` in `server/.env` and `VITE_CONTRACT_ADDRESS` in `client/.env`. Both chain IDs should be `31337`. The deployer is the administrator.

### Run the services

```bash
# Terminal C, with the Python environment active:
python server/app.py
# Terminal D:
npm --prefix client run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173`. Add a wallet network with RPC `http://127.0.0.1:8545`, chain ID `31337`, currency `ETH`. Import Hardhat test accounts into a separate **test-only** wallet profile. These keys are public; never use them with real funds. The first account is the administrator.

## Election walkthrough

1. Connect the administrator wallet and add at least two candidates in **Election admin**. Names can be edited during registration.
2. In **Voter registration**, with consent, enroll the person's ID, face and their own wallet using the administrator token. The operator must verify institutional eligibility before enrollment.
3. Approve that same wallet on-chain in **Election admin**. Biometric enrollment and wallet approval are separate steps.
4. After all voters are registered, choose **Open voting**. This permanently locks candidate details and wallet registration.
5. Connect a registered voter wallet, enable the camera in **Cast your vote**, enter the registered ID and sign the verification message. Slowly turn your head during capture.
6. Select a candidate, review and sign the transaction. A receipt appears after confirmation.
7. Close voting from the administrator wallet. Results and history remain on-chain.

A restarted local chain loses its state. Redeploy and update both configurations. V2 requires a **new contract deployment**; an old V1 contract cannot acquire these methods, and old ballots are not migrated or reset.

## Tests

```bash
npm test
python -m pytest server/tests -q
npm --prefix client run build
```

API tests use synthetic biometric samples; they do not establish camera accuracy or spoof resistance. See [review](docs/REVIEW.md) and [verification](docs/VERIFICATION.md).

## Deployment boundaries

The frontend can be hosted statically with SPA fallback to `index.html`. Flask needs a Python host with native face-recognition dependencies and persistent storage. Use HTTPS, explicit frontend origins, reachable RPC/API endpoints and a shared rate-limit backend for multiple workers (Redis also needs its Python client). Never expose an unlocked Hardhat node publicly. The included deploy command targets a local test chain only.

The verification authority is a trusted central component. The application does not encrypt the biometric database at rest; secure storage, access controls, consent/retention procedures, stronger presentation-attack detection and independent security/accessibility audits are needed before broader use.
