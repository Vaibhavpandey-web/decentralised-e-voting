# Review and implementation notes

| Original issue | Change |
| --- | --- |
| UI cycled through unused unlocked test accounts | Voter signs with their own connected wallet |
| Contract allowed any wallet to bypass biometric UI | On-chain eligibility and signed, expiring verification permits |
| Client could write a JSON voted ledger | Contract atomically tracks wallet and identity reuse |
| Unauthenticated wipe/reset routes | Destructive HTTP routes removed |
| Hard-coded frontend admin password | Contract enforces administrator wallet |
| Admin UI called missing Solidity methods | Contract, ABI and UI updated together |
| Roll number used directly in file paths | Strict ID validation and parameterized SQLite storage |
| Identity and action could match different faces | Exactly one matching face required in every capture frame |
| Hard-coded candidate labels and contract addresses | Contract reads and environment configuration |
| Missing root manifest / inconsistent Hardhat modules | Reproducible manifest, local pinned compiler, CommonJS setup |

One contract represents one election. Administrator and verifier addresses are immutable. Election phases move forward only; there is no reset. Candidate updates and wallet registration close when voting opens.

The server consumes a one-use wallet-signed challenge, checks face identity and movement, then signs `keccak256(abi.encode(chainId, contract, wallet, identityDigest, deadline))` with EIP-191. The contract validates the authority and rejects expired, wrong-domain, repeated-wallet and repeated-identity votes. The candidate choice is not sent to the biometric service; the voter chooses it in their blockchain transaction.

The secret-keyed identity digest prevents straightforward enumeration of roll-number hashes, but is not anonymous. Keep its key stable throughout an election. Wallets, vote calldata, events and counts remain publicly readable even while the UI hides final results until closing.

Remaining limits: centrally trusted biometric authority, heuristic movement detection vulnerable to replay/deepfakes, possible biometric false accepts/rejects, no encrypted biometric storage built into the application, no alternative accessible identity-verification path, and no independent security audit. An operator must validate institutional eligibility. Real camera and MetaMask acceptance testing is still required.

Legacy committed virtual-environment/model files are not changed by this focused redesign. Install fresh dependencies using the manifests rather than using that environment.

References: [Solidity signature recovery](https://docs.soliditylang.org/en/latest/solidity-by-example.html), [ethers signing](https://docs.ethers.org/v6/cookbook/signing/), [OpenZeppelin cryptography](https://docs.openzeppelin.com/contracts/5.x/api/utils#cryptography).
