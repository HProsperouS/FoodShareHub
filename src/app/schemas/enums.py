from enum import Enum
class DonationStatus(str, Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    RESERVED = 'RESERVED'
    COMPLETED = 'COMPLETED'
