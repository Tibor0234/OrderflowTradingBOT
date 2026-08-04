from data_managers.context.subscriber import ContextManagerSubscriber
from data_managers.context.utils import ContextMessage, ContextPeriod
from analyzers.context_timeframe.subscriber import ContextTimeframeSubscriber
from analyzers.context_timeframe.model import ContextTimeframe
from sessions.resource import Resource

class ContextTimeframeAnalyzer(ContextManagerSubscriber, Resource):
    def __init__(self, period: ContextPeriod, visualize=True):
        self.model: ContextTimeframe = ContextTimeframe(period)

        self.visualize = visualize
        self.subscribers: list[ContextTimeframeSubscriber] = []

    @property
    def period(self):
        return self.model.period

    @property
    def visualizer(self):
        if self.visualize:
            from visualizers.context_chart.timeframe import ContextTimeframeVisualizer
            return ContextTimeframeVisualizer(self.model)
        return None

    def reset(self):
        self.model.timeframe = None
        self.model.content.clear()

    def process_message(self, msg: ContextMessage):
        if self.model.timeframe is None:
            self.model.timeframe = msg.timeframe

        if not self.model.content:
            self.model.content = msg.candles

        for sub in self.subscribers:
            sub.on_context_timeframe_update(msg)

    def subscribe(self, subscriber: ContextTimeframeSubscriber):
        self.subscribers.append(subscriber)
        subscriber.set_period(self.model.period)
        return self