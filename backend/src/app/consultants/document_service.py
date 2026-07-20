import hashlib
import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.storage import StorageProvider
from app.models.consultant import Consultant
from app.models.document import Document
from app.consultants.enums import DocumentType
from app.auth.enums import UserRole

# Set up dedicated isolated security logger
security_logger = logging.getLogger("security_audit")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    "application/pdf", 
    "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

class DocumentService:
    """
    Coordinates atomic multi-tier binary ingestion pipelines while enforcing 
    strict perimeter defenses, fine-grained RBAC verification, and audit logs.
    """
    def __init__(self, db: AsyncSession, storage_provider: StorageProvider):
        self.db = db
        self.storage = storage_provider

    async def upload_consultant_document(
        self, 
        consultant_id: int, 
        consultant_public_id: UUID,
        document_type: DocumentType, 
        filename: str, 
        mime_type: str, 
        file_bytes: bytes,
        uploaded_by_user: any
    ) -> Document:
        """Layer 1 & 2: Validates payload footprints and stores binaries under opaque keys."""
        
        # 1. Layer 1 Perimeter Validations
        if len(file_bytes) == 0:
            security_logger.warning(f"Failed upload: Empty file rejected. User ID: {uploaded_by_user.id}")
            raise AppException(status_code=400, message="Cannot process an empty file attachment payload.")
        if len(file_bytes) > MAX_FILE_SIZE:
            security_logger.warning(f"Failed upload: Oversized file ({len(file_bytes)} bytes) rejected. User ID: {uploaded_by_user.id}")
            raise AppException(status_code=400, message="Ingested file asset exceeds structural 10MB limit controls.")
        if mime_type not in ALLOWED_MIME_TYPES:
            security_logger.warning(f"Failed upload: Unauthorized MIME type '{mime_type}' rejected. User ID: {uploaded_by_user.id}")
            raise AppException(status_code=400, message="MIME type classification is not authorized by the platform.")

        # 2. Extract SHA-256 integrity fingerprint
        checksum = hashlib.sha256(file_bytes).hexdigest()

        # 3. Assess version iteration history states
        version_query = select(Document).where(
            Document.consultant_id == consultant_id,
            Document.document_type == document_type
        )
        query_result = await self.db.execute(version_query)
        next_version_index = len(query_result.scalars().all()) + 1

        # 4. Layer 3: Opaque Storage Path Masking
        document_uuid = uuid4()
        storage_key = f"documents/consultants/{consultant_public_id}/{document_type.value.lower()}_{document_uuid}_v{next_version_index}.bin"

        # 5. Persist binary data via isolated engine abstraction
        await self.storage.upload(storage_key, file_bytes)
        security_logger.info(f"Storage success: Key {storage_key} generated for Document UUID: {document_uuid}")

        try:
            # 6. Atomic state lifecycle adjustment
            await self.db.execute(
                update(Document)
                .where(
                    Document.consultant_id == consultant_id,
                    Document.document_type == document_type,
                    Document.is_active == True
                )
                .values(is_active=False)
            )

            new_document = Document(
                consultant_id=consultant_id,
                uploaded_by=uploaded_by_user.id,
                document_type=document_type,
                storage_key=storage_key,
                original_filename=filename,
                mime_type=mime_type,
                size_bytes=len(file_bytes),
                checksum=checksum,
                version=next_version_index,
                is_active=True
            )
            
            self.db.add(new_document)
            await self.db.commit()
            await self.db.refresh(new_document)

            # Layer 4: Audit trail tracking
            security_logger.info(f"Audit Log [Upload]: Doc {new_document.public_id} initialized by User {uploaded_by_user.id}")
            return new_document

        except Exception as transaction_failure:
            await self.storage.delete(storage_key)
            await self.db.rollback()
            security_logger.error(f"Transaction failed. Opaque file key {storage_key} automatically scrubbed for safety.")
            raise transaction_failure

    async def get_secure_document_download(self, document_public_id: UUID, current_user: any) -> tuple[str, str]:
        """
        Layer 2 & 3: Validates ownership bounds and returns metadata targets.
        Guarantees actual infrastructure file paths are never exposed to clients.
        """
        stmt = select(Document).where(
            Document.public_id == document_public_id,
            Document.deleted_at == None
        )
        result = await self.db.execute(stmt)
        document = result.scalars().first()

        if not document:
            raise AppException(status_code=404, message="Document not found.")

        # Fetch parent profile to verify cross-entity ownership boundaries
        consultant_stmt = select(Consultant).where(Consultant.id == document.consultant_id)
        consultant_res = await self.db.execute(consultant_stmt)
        consultant = consultant_res.scalars().first()

        # Fine-Grained Authorization Logic: Admins/Managers always pass; Recruiters must own the record
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            if consultant.recruiter_id != current_user.id:
                security_logger.warning(
                    f"Security Alert [Unauthorized Download Attempt]: User {current_user.id} "
                    f"blocked from downloading Document {document_public_id} owned by Recruiter {consultant.recruiter_id}"
                )
                raise AppException(status_code=403, message="Access denied to requested document.")

        security_logger.info(f"Audit Log [Download Approved]: Doc {document_public_id} accessed by User {current_user.id}")
        
        # Return the secure internal key and filename back to the streaming delivery layer
        return document.storage_key, document.original_filename