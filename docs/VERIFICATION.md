# Verification — 19 October 2026

Story: administrator setup → approved voter wallet → identity verification → candidate review → on-chain transaction → confirmed receipt.

| Check | Result | Evidence / boundary |
| --- | --- | --- |
| Solidity suite | Passed | 11 tests: access control, election phases, readiness, candidate validation, duplicate wallet/identity, expired/forged/wrong-domain permits |
| Flask API suite | Passed | 6 tests: supervised enrollment, duplicate records, removed destructive routes, wallet signatures, one-use/expired challenges, movement and every-frame identity checks |
| Vue production build | Passed | Vite production assets generated successfully |
| Browser voting flow | Passed with simulated biometric authority | Browser wallet adapter signed through local Hardhat; simulated camera/verification permit; real contract vote persisted; confirmed receipt rendered |
| Repeat voting UI | Passed | Returning to voting booth displayed “You’ve already voted” |
| Mobile layouts | Passed | All four routes had no document overflow at 390px width |
| Wallet unavailable | Passed | User-facing install-wallet guidance rendered |
| Browser JavaScript errors | None observed | No page errors during the tested flow |
| Real face recognition / physical webcam / MetaMask | Not verified | Requires manual acceptance testing; automated tests use synthetic face samples and a wallet adapter |
| Public deployment | Not performed | Contract tested on a local chain only; new deployment and service configuration required |
| GitHub publication | Access restored | Branch creation succeeded after the GitHub App installation was updated; publishing the reviewed changes |

The desktop/mobile/ballot PNGs show the local test election, not a public deployed site. The biometric service remains a trusted authority. These checks are not a security audit or proof of secret-ballot suitability.
