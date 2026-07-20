from enum import Enum

class CommunicationType(str, Enum):
    EMAIL = "EMAIL"
    PHONE_CALL = "PHONE_CALL"
    MEETING = "MEETING"
    SMS = "SMS"
    SLACK = "SLACK"
    TEAMS = "TEAMS"
    INTERNAL_NOTE = "INTERNAL_NOTE"
    SYSTEM_EVENT = "SYSTEM_EVENT"

class CommunicationDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    INTERNAL = "INTERNAL"