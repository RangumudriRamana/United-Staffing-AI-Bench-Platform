from enum import Enum

class RequirementStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    SOURCING = "SOURCING"
    SUBMITTING = "SUBMITTING"
    INTERVIEWING = "INTERVIEWING"
    ON_HOLD = "ON_HOLD"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"

class WorkModel(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"

class RequirementPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"