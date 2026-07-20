from enum import Enum

class IntegrationType(str, Enum):
    EMAIL = "EMAIL"
    CALENDAR = "CALENDAR"
    ATS = "ATS"
    VMS = "VMS"
    CRM = "CRM"
    WEBHOOK = "WEBHOOK"
    STORAGE = "STORAGE"
    AI = "AI"
    MESSAGING = "MESSAGING"

class IntegrationStatus(str, Enum):
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    DISCONNECTED = "DISCONNECTED"
    SUSPENDED = "SUSPENDED"

class SyncStatus(str, Enum):
    SYNCHRONIZED = "SYNCHRONIZED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"