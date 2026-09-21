from unittest.mock import MagicMock

from app.vendors.dependencies import get_vendor_service
from app.vendors.service import VendorService


def test_get_vendor_service():
    db = MagicMock()

    service = get_vendor_service(db)

    assert isinstance(service, VendorService)
    assert service.db is db