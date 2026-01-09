// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PrajaNetraIntegrity {
    struct ComplaintManifest {
        bytes32 manifestHash;
        uint256 timestamp;
        bool exists;
    }

    mapping(uint256 => ComplaintManifest) public registry;
    address public admin;

    event ManifestAnchored(uint256 indexed complaintId, bytes32 manifestHash);

    constructor() {
        admin = msg.sender;
    }

    function anchorManifest(uint256 _complaintId, bytes32 _manifestHash) public {
        require(!registry[_complaintId].exists, "Complaint already anchored");

        registry[_complaintId] = ComplaintManifest({
            manifestHash: _manifestHash,
            timestamp: block.timestamp,
            exists: true
        });

        emit ManifestAnchored(_complaintId, _manifestHash);
    }

    function verifyManifest(uint256 _complaintId) public view returns (bytes32) {
        return registry[_complaintId].manifestHash;
    }
}