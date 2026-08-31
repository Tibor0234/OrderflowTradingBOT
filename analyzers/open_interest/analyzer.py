from decimal import Decimal

from session_pairs.resource import Resource
from data_managers.open_interest.subscriber import OpenInterestManagerSubscriber
from data_managers.open_interest.utils import OpenInterestMessage
from analyzers.open_interest.model import OpenInterest
from analyzers.utils import OscillatorRecord

class OpenInterestAnalyzer(Resource, OpenInterestManagerSubscriber):
    def __init__(self, aggregation_minutes, length=50, visualize=True):
        if aggregation_minutes < 1:
            raise ValueError("aggregation_minutes must be at least 1")

        self.model: OpenInterest = OpenInterest(length)
        self.aggregation_minutes = aggregation_minutes
        self._aggregation_values: list[Decimal] = []
        self._aggregation_start_time: int | None = None
        self.visualize = visualize

    @property
    def visualizer(self):
        if self.visualize:
            from visualizers.price_chart.open_interest import OpenInterestVisualizer
            return OpenInterestVisualizer(self.model, self.aggregation_minutes)
        return None

    def reset(self):
        self.model.history.clear()
        self.model.current = None
        self._aggregation_values.clear()
        self._aggregation_start_time = None

    def process_message(self, msg: OpenInterestMessage):
        self.model.current = OscillatorRecord(
            time=msg.time,
            value=msg.open_interest
        )

        if not self._aggregation_values:
            self._aggregation_start_time = msg.time

        self._aggregation_values.append(msg.open_interest)

        if len(self._aggregation_values) < self.aggregation_minutes:
            return

        self.model.history.append(OscillatorRecord(
            time=self._aggregation_start_time,
            value=sum(self._aggregation_values, Decimal(0)) / len(self._aggregation_values)
        ))
        self._aggregation_values.clear()
        self._aggregation_start_time = None