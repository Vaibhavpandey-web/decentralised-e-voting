const { expect } = require("chai");
const { ethers } = require("hardhat");
const {
  loadFixture,
  time,
} = require("@nomicfoundation/hardhat-network-helpers");
async function setup() {
  const [admin, verifier, voter, other] = await ethers.getSigners();
  const c = await (
    await ethers.getContractFactory("Voting")
  ).deploy("Campus Council", verifier.address);
  await c.addCandidate("Ananya Sharma");
  await c.addCandidate("Arjun Mehta");
  await c.registerVoter(voter.address);
  await c.registerVoter(other.address);
  return { c, admin, verifier, voter, other };
}
async function permit(c, verifier, voter, o = {}) {
  const identity = o.identity || ethers.id("voter-001"),
    deadline = o.deadline ?? (await time.latest()) + 300;
  const { chainId } = await ethers.provider.getNetwork();
  const digest = ethers.keccak256(
    ethers.AbiCoder.defaultAbiCoder().encode(
      ["uint256", "address", "address", "bytes32", "uint256"],
      [
        o.chainId ?? chainId,
        o.contract ?? (await c.getAddress()),
        voter.address,
        identity,
        deadline,
      ]
    )
  );
  return [
    identity,
    deadline,
    await verifier.signMessage(ethers.getBytes(digest)),
  ];
}
describe("Voting security and lifecycle", () => {
  it("records a verified ballot once", async () => {
    const { c, verifier, voter } = await loadFixture(setup);
    await c.openVoting();
    const p = await permit(c, verifier, voter);
    await expect(c.connect(voter).vote(1, ...p))
      .to.emit(c, "VoteCast")
      .withArgs(voter.address, 1);
    expect(await c.totalVotes()).to.equal(1);
    expect((await c.candidates(1)).voteCount).to.equal(1);
    await expect(c.connect(voter).vote(2, ...p)).to.be.revertedWith(
      "Already voted"
    );
  });
  it("blocks unregistered callers", async () => {
    const { c, admin, verifier } = await loadFixture(setup);
    await c.openVoting();
    await expect(
      c.vote(1, ...(await permit(c, verifier, admin)))
    ).to.be.revertedWith("Voter not registered");
  });
  it("rejects forged verification", async () => {
    const { c, other, voter } = await loadFixture(setup);
    await c.openVoting();
    await expect(
      c.connect(voter).vote(1, ...(await permit(c, other, voter)))
    ).to.be.revertedWith("Invalid verification");
  });
  it("rejects wallet-swapped permits", async () => {
    const { c, verifier, voter, other } = await loadFixture(setup);
    await c.openVoting();
    await expect(
      c.connect(other).vote(1, ...(await permit(c, verifier, voter)))
    ).to.be.revertedWith("Invalid verification");
  });
  it("rejects cross-chain and cross-contract replay", async () => {
    const { c, verifier, voter, other } = await loadFixture(setup);
    await c.openVoting();
    for (const o of [{ chainId: 1 }, { contract: other.address }])
      await expect(
        c.connect(voter).vote(1, ...(await permit(c, verifier, voter, o)))
      ).to.be.revertedWith("Invalid verification");
  });
  it("rejects expired permits", async () => {
    const { c, verifier, voter } = await loadFixture(setup);
    await c.openVoting();
    await expect(
      c
        .connect(voter)
        .vote(
          1,
          ...(await permit(c, verifier, voter, {
            deadline: (await time.latest()) - 1,
          }))
        )
    ).to.be.revertedWith("Invalid or expired permit");
  });
  it("prevents the same identity voting from another wallet", async () => {
    const { c, verifier, voter, other } = await loadFixture(setup);
    await c.openVoting();
    await c.connect(voter).vote(1, ...(await permit(c, verifier, voter)));
    await expect(
      c.connect(other).vote(2, ...(await permit(c, verifier, other)))
    ).to.be.revertedWith("Already voted");
  });
  it("restricts administrator actions", async () => {
    const { c, other } = await loadFixture(setup);
    for (const [m, a] of [
      ["addCandidate", ["Fake"]],
      ["updateCandidateName", [1, "Fake"]],
      ["registerVoter", [other.address]],
      ["openVoting", []],
      ["closeVoting", []],
    ])
      await expect(c.connect(other)[m](...a)).to.be.revertedWith("Admin only");
  });
  it("locks registration when voting opens", async () => {
    const { c, admin } = await loadFixture(setup);
    await c.openVoting();
    for (const [m, a] of [
      ["addCandidate", ["Late"]],
      ["updateCandidateName", [1, "Late"]],
      ["registerVoter", [admin.address]],
      ["openVoting", []],
    ])
      await expect(c[m](...a)).to.be.revertedWith("Registration closed");
  });
  it("validates candidates and cannot reopen a closed election", async () => {
    const { c, verifier, voter } = await loadFixture(setup);
    const p = await permit(c, verifier, voter);
    await expect(c.connect(voter).vote(1, ...p)).to.be.revertedWith(
      "Voting not open"
    );
    await c.openVoting();
    for (const id of [0, 3])
      await expect(c.connect(voter).vote(id, ...p)).to.be.revertedWith(
        "Invalid candidate"
      );
    await c.closeVoting();
    await expect(c.connect(voter).vote(1, ...p)).to.be.revertedWith(
      "Voting not open"
    );
    await expect(c.openVoting()).to.be.revertedWith("Registration closed");
  });
  it("validates readiness, names and duplicate registration", async () => {
    const { c, verifier, voter } = await loadFixture(setup);
    for (const name of ["", "x".repeat(101)])
      await expect(c.addCandidate(name)).to.be.revertedWith("Invalid name");
    await expect(c.registerVoter(voter.address)).to.be.revertedWith(
      "Invalid or registered voter"
    );
    const empty = await (
      await ethers.getContractFactory("Voting")
    ).deploy("Empty", verifier.address);
    await expect(empty.openVoting()).to.be.revertedWith("Election not ready");
  });
});
