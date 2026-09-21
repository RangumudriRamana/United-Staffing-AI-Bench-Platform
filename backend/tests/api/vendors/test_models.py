from unittest.mock import MagicMock

from app.vendors.models import Client


def test_client_vendor_public_id_returns_vendor_public_id():
    client = Client()
    vendor = MagicMock()
    vendor.public_id = "vendor-123"
    client.vendor = vendor

    assert client.vendor_public_id == "vendor-123"


def test_client_vendor_public_id_returns_none_without_vendor():
    client = Client()
    client.vendor = None

    assert client.vendor_public_id is None