require("@nomicfoundation/hardhat-toolbox");
const { subtask } = require("hardhat/config");
const {
  TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD,
} = require("hardhat/builtin-tasks/task-names");
subtask(TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD).setAction(
  async ({ solcVersion }, _, runSuper) =>
    solcVersion === "0.8.24"
      ? {
          compilerPath: require.resolve("solc/soljson.js"),
          isSolcJs: true,
          version: solcVersion,
          longVersion: require("solc").version(),
        }
      : runSuper()
);
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 } },
  },
  networks: {
    localhost: { url: "http://127.0.0.1:8545" },
    ...(process.env.SEPOLIA_RPC_URL ? {
      sepolia: {
        url: process.env.SEPOLIA_RPC_URL,
        chainId: 11155111,
        accounts: process.env.DEPLOYER_PRIVATE_KEY ? [process.env.DEPLOYER_PRIVATE_KEY] : [],
      },
    } : {}),
  },
};
