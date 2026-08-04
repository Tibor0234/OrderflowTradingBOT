from enum import Enum
from dataclasses import dataclass

class EventType(Enum):
    OI = 'api_oi'
    OB = 'api_ob'
    TR = 'ws_tr'
    NWS = 'nws'
    CTX = 'ctx'

@dataclass(slots=True)
class SessionCounter:
    current: int
    total: int