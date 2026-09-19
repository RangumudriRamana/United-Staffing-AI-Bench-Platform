from faker import Faker

from app.vendors.models import (
    Vendor,
    VendorContact,
    Client,
)

from app.vendors.enums import (
    VendorStatus,
    VendorTier,
    VendorType,
    ClientStatus,
)

fake = Faker()


class VendorFactory:
    """
    Builds transient Vendor entities.

    Objects are NOT persisted.
    """

    @staticmethod
    def build(**kwargs) -> Vendor:

        defaults = {
            "name": fake.unique.company(),
            "vendor_type": VendorType.PRIME_VENDOR,
            "tier": VendorTier.TIER_2,
            "status": VendorStatus.ACTIVE,
            "website": fake.url(),
            "preferred": False,
            "notes": fake.sentence(),
            "created_by": 1,
            "updated_by": None,
        }

        defaults.update(kwargs)

        return Vendor(**defaults)


class VendorContactFactory:
    """
    Builds transient VendorContact entities.
    """

    @staticmethod
    def build(**kwargs) -> VendorContact:

        defaults = {
            "vendor_id": 1,
            "name": fake.name(),
            "title": fake.job(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "linkedin": fake.url(),
            "timezone": "EST",
            "preferred_contact": False,
            "is_active": True,
        }

        defaults.update(kwargs)

        return VendorContact(**defaults)


class ClientFactory:
    """
    Builds transient Client entities.
    """

    @staticmethod
    def build(**kwargs) -> Client:

        defaults = {
            "vendor_id": 1,
            "created_by": 1,
            "updated_by": None,
            "name": fake.company(),
            "display_name": fake.company_suffix(),
            "industry": "Information Technology",
            "website": fake.url(),
            "primary_location": "Dallas, TX",
            "timezone": "EST",
            "notes": fake.sentence(),
            "status": ClientStatus.ACTIVE,
            "preferred": False,
        }

        defaults.update(kwargs)

        return Client(**defaults)