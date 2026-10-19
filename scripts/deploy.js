const hre = require("hardhat");
const fs = require("node:fs");
async function main() {
  const verifier = process.env.VERIFIER_ADDRESS;
  if (!hre.ethers.isAddress(verifier || ""))
    throw Error(
      "Set VERIFIER_ADDRESS to the server verification signer address."
    );
  const c = await (
    await hre.ethers.getContractFactory("Voting")
  ).deploy(process.env.ELECTION_TITLE || "Campus Council Election", verifier);
  await c.waitForDeployment();
  const address = await c.getAddress();
  const { chainId } = await hre.ethers.provider.getNetwork();
  const artifact = await hre.artifacts.readArtifact("Voting");
  fs.writeFileSync(
    "client/src/Voting.json",
    JSON.stringify({ abi: artifact.abi }, null, 2) + "\n"
  );
  fs.writeFileSync(
    "deployment.local.json",
    JSON.stringify({ address, chainId: Number(chainId), verifier }, null, 2)
  );
  console.log(
    `Contract: ${address}\nChain: ${chainId}\nSet CONTRACT_ADDRESS in server/.env and VITE_CONTRACT_ADDRESS in client/.env.`
  );
}
main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
