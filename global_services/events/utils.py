from enum import Enum

class EventBusMsgType(Enum):
    SESSION_START = 'session_start'
    SESSION_END = 'session_end'
    PROCESS_END = 'process_end'
    
    CANDLE_CLOSE = 'candle_close'
    BIG_TRADE = 'big_trade'
    TRADE_CLOSE = 'trade_close'

    PRICE_UPDATE = 'price_update'
    TRADE_ADDED = 'trade_added'
    TRADE_REMOVED = 'trade_removed'