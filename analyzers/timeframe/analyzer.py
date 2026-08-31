from session_pairs.resource import Resource
from data_managers.trade.subscriber import TradeManagerSubscriber
from data_managers.trade.utils import TradeMessage
from analyzers.timeframe.subscriber import TimeframeSubscriber

from analyzers.timeframe.model import Timeframe
from analyzers.timeframe.candle import Candle

from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType

class TimeframeAnalyzer(Resource, TradeManagerSubscriber):
    def __init__(self, candle_seconds, length=200, visualize=True):
        self.model: Timeframe = Timeframe(length)

        self.visualize = visualize

        self.candle_seconds = candle_seconds
        self.candle_ms = candle_seconds * 1000

        self.subscribers: list[TimeframeSubscriber] = []

    @property
    def visualizer(self):
        if self.visualize:
            from visualizers.price_chart.timeframe import TimeframeVisualizer
            return TimeframeVisualizer(self.model, self.candle_seconds)
        return None

    def subscribe(self, subscriber: TimeframeSubscriber):
        subscriber.init_model(self.model.history.maxlen)
        self.subscribers.append(subscriber)
        return self

    def reset(self):
        self.model.history.clear()
        self.model.current = None

    def process_message(self, msg: TradeMessage):
        if self.model.current is None:
            self.model.current = Candle(
                time=msg.time,
                open=msg.price
            )
        else:
            self.model.current.update_candle(msg.price)

        for sub in self.subscribers:
            sub.on_timeframe_update(msg)

        if msg.time - self.model.current.time >= self.candle_ms:
            next_open = self.model.current.time + self.candle_ms
            self.model.history.append(self.model.current)

            for sub in self.subscribers:
                sub.on_candle_close(next_open)

            self.model.current = Candle(
                time=next_open,
                open=msg.price
            )

            EventBus().emit(
                EventBusMsgType.CANDLE_CLOSE,
                self.candle_seconds
            )