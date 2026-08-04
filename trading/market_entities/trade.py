from __future__ import annotations
import uuid
from decimal import Decimal
from trading.market_entities.utils import Side
from trading.market_entities.order import Order
from trading.market_entities.stop_order import StopOrder
from trading.market_entities.increase_order import IncreaseOrder
from global_services.data.provider import DataProvider

class Trade:
    @classmethod
    def convert_from_order(cls, order: Order, execution_price, value) -> Trade:
        return cls(
            id=order.id,
            execution_price=execution_price,
            side=order.side,
            value=value,
            leverage=order.leverage,
        )

    def __init__(self, id: uuid.UUID, execution_price, side: Side, value, leverage):
        self.id = id
        self.execution_price = execution_price
        self.side = side
        self.value = value
        self.leverage = leverage
        self.realized_pnl = 0
        self.open_time = DataProvider().get_time()
    
    def link(self, linked_order: IncreaseOrder | StopOrder):
        linked_order.set_from_source(self.id, self.side)
        return self
    
    def link_many(self, linked_orders: list[IncreaseOrder | StopOrder]):
        if not isinstance(linked_orders, list):
            linked_orders = [linked_orders]
        
        for linked_order in linked_orders:
            self.link(linked_order)
            
        return self

    def update_on_fill(self, execution_price: Decimal, value: Decimal, leverage: Decimal):
        total_value = self.value + value
    
        self.execution_price = (self.execution_price * self.value + execution_price * value) / total_value
        self.leverage = (self.leverage * self.value + leverage * value) / total_value
        self.value = total_value

    @property
    def floating_pnl(self):
        price = DataProvider().get_price()
        return self.floating_pnl_from_price(price)

    def floating_pnl_from_price(self, price: Decimal):
        return (price - self.execution_price) * self.side.value * (self.value * self.leverage) / self.execution_price
    
    def charge_fee(self, fee_rate: Decimal):
        return self.charge_fee_from_value(self.value, fee_rate)

    def charge_fee_from_value(self, value, fee_rate: Decimal):
        fee = (value * self.leverage) * fee_rate
        self.realized_pnl -= fee

        return fee

    def close_trade_partial(self, execuiton_price: Decimal, close_rate: Decimal):
        float_pnl = self.floating_pnl_from_price(execuiton_price)

        closed_value = self.value * close_rate
        self.value -= closed_value

        realized = float_pnl * close_rate
        self.realized_pnl += realized

        return closed_value, realized
    
    def is_active(self):
        return self.value > 0
    
    def close_trade(self):
        self.close_time = DataProvider().get_time()