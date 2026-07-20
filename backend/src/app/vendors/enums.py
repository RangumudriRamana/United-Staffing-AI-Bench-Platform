from enum import Enum

class VendorType(str, Enum):
    PRIME_VENDOR = "PRIME_VENDOR"
    IMPLEMENTER = "IMPLEMENTER"
    DIRECT_CLIENT = "DIRECT_CLIENT"
    SUB_VENDOR = "SUB_VENDOR"

class VendorTier(str, Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"
    STRATEGIC = "STRATEGIC"

class VendorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLACKLISTED = "BLACKLISTED"

class ClientStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PROSPECT = "PROSPECT"
    BLACKLISTED = "BLACKLISTED"
    ARCHIVED = "ARCHIVED"