import json
import hashlib
from web3 import Web3
from app.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
        self.account = self.w3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
        self.contract_address = settings.CONTRACT_ADDRESS

        # COMPLETE ABI including the ManifestAnchored Event
        self.abi = json.loads("""
                [
                    {
                        "anonymous": false,
                        "inputs": [
                            {"indexed": true, "internalType": "uint256", "name": "complaintId", "type": "uint256"},
                            {"indexed": false, "internalType": "bytes32", "name": "manifestHash", "type": "bytes32"}
                        ],
                        "name": "ManifestAnchored",
                        "type": "event"
                    },
                    {
                        "inputs": [
                            {"internalType": "uint256", "name": "_complaintId", "type": "uint256"},
                            {"internalType": "bytes32", "name": "_manifestHash", "type": "bytes32"}
                        ],
                        "name": "anchorManifest",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [{"internalType": "uint256", "name": "_complaintId", "type": "uint256"}],
                        "name": "verifyManifest",
                        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                """)
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def generate_manifest_hash(self, complaint_data: dict, evidence_hashes: list) -> str:
        """Creates a deterministic fingerprint. Uses UNIX timestamp for 100% consistency."""

        # Convert datetime to integer UNIX timestamp
        dt = complaint_data['filed_at']
        timestamp_int = int(dt.timestamp())

        manifest = {
            "id": int(complaint_data['id']),
            "description_hash": hashlib.sha256(complaint_data['description'].encode()).hexdigest(),
            "evidence_inventory": sorted([str(h) for h in evidence_hashes]),
            "initial_severity": int(complaint_data['severity']),
            "timestamp": timestamp_int  # Use Integer, not String
        }

        # Ensure JSON keys are sorted and no extra whitespace
        manifest_string = json.dumps(manifest, sort_keys=True, separators=(',', ':'))

        # Debug log to see exactly what we are hashing (Check this in Celery logs)
        logger.info(f"🧬 Hashing Manifest: {manifest_string}")

        return self.w3.keccak(text=manifest_string).hex()

    async def verify_integrity(self, complaint_id: int, current_manifest_hash: str) -> bool:
        """Robust case-insensitive verification."""
        try:
            on_chain_hash_bytes = self.contract.functions.verifyManifest(complaint_id).call()
            on_chain_hex = on_chain_hash_bytes.hex()

            # Ensure both have 0x prefix and are lowercase for comparison
            def normalize(h):
                h = h.lower()
                return h if h.startswith("0x") else "0x" + h

            is_valid = normalize(on_chain_hex) == normalize(current_manifest_hash)

            if not is_valid:
                logger.error(
                    f"❌ MISMATCH: On-chain({normalize(on_chain_hex)}) vs Current({normalize(current_manifest_hash)})")

            return is_valid
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False

    async def anchor_to_blockchain(self, complaint_id: int, manifest_hash: str):
        """Sends the hash to the Smart Contract (keep existing logic)."""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address,
                                                      'pending')  # Use 'pending' to avoid nonce gaps
            txn = self.contract.functions.anchorManifest(
                complaint_id,
                Web3.to_bytes(hexstr=manifest_hash)
            ).build_transaction({
                'chainId': 1337,
                'gas': 500000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'nonce': nonce,
            })
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=settings.BLOCKCHAIN_PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            return self.w3.to_hex(tx_hash)
        except Exception as e:
            logger.error(f"Anchoring failed: {e}")
            return None


blockchain_service = BlockchainService()