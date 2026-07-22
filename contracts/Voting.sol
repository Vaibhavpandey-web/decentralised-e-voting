// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    struct Candidate {
        uint256 id;
        string name;
        uint256 voteCount;
    }

    mapping(uint256 => Candidate) public candidates;
    mapping(address => bool) public hasVoted; 
    
    uint256 public candidatesCount;
    address public admin;

    constructor() {
        admin = msg.sender;
        
        // ADD YOUR REAL CANDIDATES HERE
        addCandidate("Narendra Modi (BJP)");
        addCandidate("Rahul Gandhi (INC)");
        addCandidate("NOTA");
    }

    function addCandidate(string memory _name) private {
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
    }

    function vote(uint256 _candidateId) public {
        require(!hasVoted[msg.sender], "Error: Voter has already cast a ballot.");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate ID.");

        hasVoted[msg.sender] = true;
        candidates[_candidateId].voteCount++;
    }
}