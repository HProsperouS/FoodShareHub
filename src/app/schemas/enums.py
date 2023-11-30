from enum import Enum
class DonationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESERVED = "RESERVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
