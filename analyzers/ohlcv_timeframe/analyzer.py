from data_managers.ohlcv.subscriber import OHLCVManagerSubscriber
from data_managers.ohlcv.utils import OHLCVMessage, OHLCVPeriod
from analyzers.ohlcv_timeframe.subscriber import OHLCVTimeframeSubscriber
from analyzers.ohlcv_timeframe.model import OHLCVTimeframe
from session_pairs.resource import Resource

class OHLCVTimeframeAnalyzer(OHLCVManagerSubscriber, Resource):
    def __init__(self, period: OHLCVPeriod, visualize=True):
        self.model: OHLCVTimeframe = OHLCVTimeframe(period)

        self.visualize = visualize
        self.subscribers: list[OHLCVTimeframeSubscriber] = []

    @property
    def period(self):
        return self.model.period

    @property
    def visualizer(self):
        if self.visualize:
            from visualizers.context_chart.timeframe import OHLCVTimeframeVisualizer
            return OHLCVTimeframeVisualizer(self.model)
        return None

    def reset(self):
        self.model.timeframe = None
        self.model.content.clear()

    def process_message(self, msg: OHLCVMessage):
        if self.model.timeframe is None:
            self.model.timeframe = msg.timeframe

        if not self.model.content:
            self.model.content = msg.candles

        for sub in self.subscribers:
            sub.on_ohlcv_timeframe_update(msg)

    def subscribe(self, subscriber: OHLCVTimeframeSubscriber):
        self.subscribers.append(subscriber)
        subscriber.set_period(self.model.period)
        return self