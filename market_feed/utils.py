from enum import Enum
from dataclasses import dataclass

class EventType(Enum):
    OI = 'api_oi'
    OB = 'api_ob'
    TR = 'ws_tr'
    NWS = 'nws'
    OHLCV = 'ohlcv'

@dataclass(slots=True)
class SessionCounter:
    session: int | None
    pair: int
    session_pair: int
    total_sessions: int
    total_pairs: int
    total_session_pairs: int