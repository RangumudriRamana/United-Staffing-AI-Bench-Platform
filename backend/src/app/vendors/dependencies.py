from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.vendors.service import VendorService

from fastapi import Depends


def get_vendor_service(
    db: AsyncSession = Depends(get_db),
) -> VendorService:
    """
    Dependency provider for VendorService.
    """

    return VendorService(db)
