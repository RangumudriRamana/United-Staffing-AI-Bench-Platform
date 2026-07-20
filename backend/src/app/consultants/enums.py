from enum import Enum

class VisaStatus(str, Enum):
    H1B = "H1B"
    H4_EAD = "H4 EAD"
    GC = "GC"
    USC = "USC"
    OPT = "OPT"
    STEM_OPT = "STEM OPT"
    CPT = "CPT"
    L2_EAD = "L2 EAD"
    TN = "TN"
    E3 = "E3"
    OTHER = "Other"

class MarketingStatus(str, Enum):
    AVAILABLE = "Available"
    MARKETING = "Marketing"
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    PLACED = "Placed"
    HOLD = "Hold"
    INACTIVE = "Inactive"

class RateType(str, Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    MONTHLY = "Monthly"
    ANNUAL = "Annual"

class ProficiencyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class DocumentType(str, Enum):
    RESUME = "Resume"
    WORK_AUTHORIZATION = "Work Authorization"
    PASSPORT = "Passport"
    DRIVER_LICENSE = "Driver License"
    VISA = "Visa"
    I94 = "I-94"
    SSN = "SSN"
    VENDOR_RTR = "Vendor RTR"
    RATE_CONFIRMATION = "Rate Confirmation"
    MISCELLANEOUS = "Miscellaneous"

class MarketingStatus(str, Enum):
    NEW = "NEW"
    READY_FOR_MARKETING = "READY_FOR_MARKETING"
    MARKETING_ACTIVE = "MARKETING_ACTIVE"
    INTERVIEWING = "INTERVIEWING"
    OFFER_PENDING = "OFFER_PENDING"
    PLACED = "PLACED"
    ON_PROJECT = "ON_PROJECT"
    UNAVAILABLE = "UNAVAILABLE"
    INACTIVE = "INACTIVE"

class AvailabilityStatus(str, Enum):
    AVAILABLE_NOW = "AVAILABLE_NOW"
    AVAILABLE_ON_DATE = "AVAILABLE_ON_DATE"
    NOT_AVAILABLE = "NOT_AVAILABLE"