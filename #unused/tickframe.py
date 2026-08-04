from collections import deque
from model_component.candle import Candle
from sessions.session_based_object import SessionBasedObject
from event_bus import EventBus
from utils import EventBusMsgType
from market_data_managers.trade_manager import TradeManagerSubscriber, TradeMessage
from model.timeframe import TimeframeSubscriber

class Tickframe(SessionBasedObject, TradeManagerSubscriber):
    def __init__(self, candle_ticks, length=200, visualize=True):
        self.symbol = None
        self.visualize = visualize

        self.candle_ticks = candle_ticks

        self.content: deque[Candle] = deque(maxlen=length-1)
        self.current_candle: Candle | None = None

        self.ticks = 0

        self.subscribers: list[TimeframeSubscriber] = []

    @property
    def visualizer(self):
        if self.visualize:
            from visualizer.timeframe_visualizer import TimeframeVisualizer
            return TimeframeVisualizer(self)
        return None

    def set_event_bus(self, event_bus: EventBus):
        self.event_bus = event_bus

    def subscribe(self, subscriber: TimeframeSubscriber):
        subscriber.init_content(self.content.maxlen)
        self.subscribers.append(subscriber)
        return self

    def reset(self):
        self.symbol = None
        self.content.clear()
        self.current_candle = None
        self.ticks = 0

    def process_message(self, msg: TradeMessage):
        if self.symbol is None:
            self.symbol = msg.symbol

        self.ticks += 1

        if self.current_candle is None:
            self.current_candle = Candle(open_time=msg.time, open=msg.price)
        else:
            self.current_candle.update_candle(msg.price)

        for sub in self.subscribers:
            sub.on_timeframe_update(msg)

        if self.ticks >= self.candle_ticks:
            self.content.append(self.current_candle)

            for sub in self.subscribers:
                sub.on_candle_close()

            self.current_candle = Candle(open_time=msg.time, open=msg.price)

            self.event_bus.emit(
                EventBusMsgType.CANDLE_CLOSE,
                msg.time / 1000,
                self.symbol,
                f"{self.candle_ticks}t"
            )

            self.ticks = 0

    def get_current_price(self):
        return self.current_candle.close if self.current_candle is not None else None