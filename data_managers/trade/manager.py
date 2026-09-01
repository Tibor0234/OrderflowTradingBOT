from decimal import Decimal
from data_managers.trade.utils import TradeMessage
from trading.market_entities.utils import Side
from data_managers.base import DataManager
from data_managers.trade.subscriber import TradeManagerSubscriber
from global_services.data.provider import DataProvider
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType

class TradeManager(DataManager):
    def __init__(self):
        self.subscribers: list[TradeManagerSubscriber] = []

    def subscribe(self, subscriber: TradeManagerSubscriber):
        self.subscribers.append(subscriber)
        return self

    def forward_message(self, msg):
        conv_msg = TradeMessage(
            time=int(msg["E"]),
            price=Decimal(msg["p"]),
            quantity=Decimal(msg["q"]),
            side=Side.SELL if msg["m"] else Side.BUY
        )

        DataProvider().set(msg['s'].upper(), conv_msg.price, conv_msg.time)
        for sub in self.subscribers:
            sub.process_message(conv_msg)

        EventBus().emit(EventBusMsgType.PRICE_UPDATE)