from enum import Enum

class Side(Enum):
    BUY = 1
    SELL = -1

    def opposite(self):
        return Side.BUY if self == Side.SELL else Side.SELL

class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'