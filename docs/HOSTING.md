# Complete hosted deployment

Frontend: https://decentralised-e-voting.vercel.app

The frontend alone does not enable voting. Complete the following setup before
enrolling any real voters. Use test participants with informed consent.

## Biometric API on Render

Create a Docker web service from this repository, branch `codex/evoting-redesign`.
Set root directory `server`, Dockerfile `./Dockerfile`, health check `/health`,
and mount a persistent disk at `/var/data`. Persistent disks require a paid
service; review its price before creating it. Use one instance and one Gunicorn
worker; the bundled configuration supplies this. Do not use ephemeral SQLite.

Set these secret environment variables in the hosting dashboard:

- `ADMIN_TOKEN`: independent random string of at least 32 characters.
- `IDENTITY_SECRET`: separate random string of at least 32 characters; keep it
  stable across deployments and back it up securely.
- `VERIFIER_PRIVATE_KEY`: a separate Ethereum signing key, never a funded wallet
  key. Derive its public address for the contract deployment.
- `CONTRACT_ADDRESS`: the new contract address, after deployment.
- `CHAIN_ID`: `11155111` for Sepolia.
- `DATABASE_PATH`: `/var/data/voters.sqlite3`.
- `ALLOWED_ORIGINS`: `https://decentralised-e-voting.vercel.app`.

Do not paste secrets in chat or commit them. The verifier private key belongs
only on the backend. The administrator token must only be given to authorized
enrollment operators. Never put either into VITE variables.

The disk persists enrollment and one-use challenges. Back it up using a
SQLite-aware backup, and test restoration. The app does not encrypt biometric
templates itself. In-memory rate limits reset on process restarts; configure
shared `RATE_LIMIT_STORAGE` before scaling. Face checks are CPU-intensive;
measure memory and request latency with a real camera before choosing capacity.

## Contract on Sepolia

Use a dedicated test wallet with Sepolia test ETH. The deploying wallet becomes
the immutable election administrator, so deploy from a wallet you control.
On your own trusted computer, set `SEPOLIA_RPC_URL`, `DEPLOYER_PRIVATE_KEY`, and
`VERIFIER_ADDRESS` as environment variables. Then run:

```sh
npm ci
npx hardhat run scripts/deploy.js --network sepolia
```

Hardhat reads these values from the process environment, not automatically from
the example file. Do not send the private key to anyone. The script prints the
contract address and writes ignored `deployment.local.json`. Set that address
on the backend. The configured verifier must match the backend signer.

## Connect Vercel

Set production build variables and redeploy the frontend:

- `VITE_API_URL`: the Render HTTPS service URL, without trailing slash.
- `VITE_CONTRACT_ADDRESS`: the new contract address.
- `VITE_CHAIN_ID`: `11155111`.
- `VITE_RPC_URL`: a Sepolia HTTPS JSON-RPC endpoint suitable for public browser
  use (do not expose a privileged provider credential).

Build settings: root `client`, install `npm ci`, build `npm run build`, output
`dist`. The source branch is `codex/evoting-redesign` until the PR is merged.

## Acceptance checks

1. `/health` reports `ready`; inspect logs without exposing secret values.
2. Confirm the contract administrator, verifier and chain match configuration.
3. Connect the admin wallet on Sepolia; add candidates and approve voter wallets.
4. Enroll a consenting test voter using the real camera and enrollment token.
5. Restart the API and verify enrollment persists.
6. Open voting; authenticate from the enrolled wallet and cast a test vote.
7. Verify the receipt and on-chain count. Check repeat voting is rejected.
8. Close the election and check further votes are rejected.

Do not call the system fully deployed until these checks pass. This remains an
academic prototype with publicly visible votes and a trusted biometric authority.
