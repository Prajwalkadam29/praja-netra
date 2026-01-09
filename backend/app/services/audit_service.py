from app.services.blockchain_service import blockchain_service
from app.models.complaint import Complaint
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    async def run_integrity_audit(db: AsyncSession):
        """
        Scans the blockchain for ALL anchored events and
        compares them with the current SQL database.
        """
        # 1. Fetch all 'ManifestAnchored' events from the Blockchain
        # We look from block 0 to the 'latest'
        contract = blockchain_service.contract
        event_filter = contract.events.ManifestAnchored.create_filter(fromBlock=0)
        blockchain_events = event_filter.get_all_entries()

        # Extract all Complaint IDs that exist on the blockchain
        on_chain_ids = [event['args']['complaintId'] for event in blockchain_events]

        # 2. Fetch all Complaint IDs currently in our SQL Database
        result = await db.execute(select(Complaint.id))
        db_ids = result.scalars().all()

        # 3. IDENTIFY ANOMALIES
        missing_from_db = [cid for cid in on_chain_ids if cid not in db_ids]

        # Check for Soft Deleted items that are still on-chain
        res_deleted = await db.execute(select(Complaint.id).filter(Complaint.is_deleted == True))
        soft_deleted_ids = res_deleted.scalars().all()

        return {
            "total_anchored_on_blockchain": len(on_chain_ids),
            "total_records_in_db": len(db_ids),
            "missing_records_count": len(missing_from_db),
            "illegally_deleted_ids": missing_from_db,  # Hard deleted (BAD!)
            "archived_ids": soft_deleted_ids,  # Soft deleted (Intentional)
            "audit_status": "PASS ✅" if len(missing_from_db) == 0 else "FAIL ❌"
        }


audit_service = AuditService()