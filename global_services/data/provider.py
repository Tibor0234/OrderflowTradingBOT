from decimal import Decimal

class DataProvider:
    _instance = None

    symbol: str
    price: Decimal
    time: int

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.symbol = None
            cls._instance.price = Decimal(0)
            cls._instance.time = 0
        return cls._instance

    # setters

    def set(self, symbol: str, price: Decimal, time: int):
        self.symbol = symbol
        self.price = price
        self.time = time

    def set_symbol(self, symbol: str):
        self.symbol = symbol

    def set_price(self, price: Decimal):
        self.price = price

    def set_time(self, time: int):
        self.time = time

    # getters

    def get_symbol(self) -> str:
        return self.symbol

    def get_price(self) -> Decimal:
        return self.price

    def get_time(self) -> int:
        return self.time