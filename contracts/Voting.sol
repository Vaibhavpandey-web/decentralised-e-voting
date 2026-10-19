// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {MessageHashUtils} from "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
/// @notice Academic demonstration. Wallets and vote choices are public.
contract Voting {
    enum Phase { Registration, Voting, Closed }
    struct Candidate { uint256 id; string name; uint256 voteCount; }
    address public immutable admin;
    address public immutable verifier;
    string public title;
    Phase public phase;
    uint256 public candidatesCount;
    uint256 public registeredCount;
    uint256 public totalVotes;
    mapping(uint256 => Candidate) public candidates;
    mapping(address => bool) public eligible;
    mapping(address => bool) public hasVoted;
    mapping(bytes32 => bool) public identityUsed;
    event CandidateAdded(uint256 indexed id, string name);
    event CandidateUpdated(uint256 indexed id, string name);
    event VoterRegistered(address indexed voter);
    event PhaseChanged(Phase phase);
    event VoteCast(address indexed voter, uint256 indexed candidateId);
    modifier onlyAdmin() { require(msg.sender == admin, "Admin only"); _; }
    modifier registrationOnly() { require(phase == Phase.Registration, "Registration closed"); _; }
    constructor(string memory electionTitle, address verificationSigner) {
        require(bytes(electionTitle).length > 0 && bytes(electionTitle).length <= 120, "Invalid title");
        require(verificationSigner != address(0), "Invalid verifier");
        admin = msg.sender; verifier = verificationSigner; title = electionTitle;
    }
    function addCandidate(string calldata name) external onlyAdmin registrationOnly {
        _validName(name); require(candidatesCount < 100, "Candidate limit");
        uint256 id = ++candidatesCount; candidates[id] = Candidate(id, name, 0);
        emit CandidateAdded(id, name);
    }
    function updateCandidateName(uint256 id, string calldata name) external onlyAdmin registrationOnly {
        require(id > 0 && id <= candidatesCount, "Invalid candidate"); _validName(name);
        candidates[id].name = name; emit CandidateUpdated(id, name);
    }
    function registerVoter(address voter) external onlyAdmin registrationOnly {
        require(voter != address(0) && !eligible[voter], "Invalid or registered voter");
        eligible[voter] = true; ++registeredCount; emit VoterRegistered(voter);
    }
    function openVoting() external onlyAdmin registrationOnly {
        require(candidatesCount >= 2 && registeredCount > 0, "Election not ready");
        phase = Phase.Voting; emit PhaseChanged(phase);
    }
    function closeVoting() external onlyAdmin {
        require(phase == Phase.Voting, "Voting not open"); phase = Phase.Closed; emit PhaseChanged(phase);
    }
    function vote(uint256 id, bytes32 identity, uint256 deadline, bytes calldata signature) external {
        require(phase == Phase.Voting, "Voting not open"); require(eligible[msg.sender], "Voter not registered");
        require(!hasVoted[msg.sender] && !identityUsed[identity], "Already voted");
        require(id > 0 && id <= candidatesCount, "Invalid candidate");
        require(identity != bytes32(0) && block.timestamp <= deadline, "Invalid or expired permit");
        bytes32 payload = keccak256(abi.encode(block.chainid, address(this), msg.sender, identity, deadline));
        require(ECDSA.recover(MessageHashUtils.toEthSignedMessageHash(payload), signature) == verifier, "Invalid verification");
        hasVoted[msg.sender] = true; identityUsed[identity] = true;
        ++candidates[id].voteCount; ++totalVotes; emit VoteCast(msg.sender, id);
    }
    function _validName(string memory name) private pure {
        require(bytes(name).length > 0 && bytes(name).length <= 100, "Invalid name");
    }
}
