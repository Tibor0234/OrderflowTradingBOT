from sessions.resource import Resource
from data_managers.open_interest.subscriber import OpenInterestManagerSubscriber
from data_managers.open_interest.utils import OpenInterestMessage
from analyzers.open_interest.model import OpenInterest
from analyzers.utils import OscillatorRecord

class OpenInterestAnalyzer(Resource, OpenInterestManagerSubscriber):
    def __init__(self, length=50, visualize=True):
        self.model: OpenInterest = OpenInterest(length)
        self.visualize = visualize

    @property
    def visualizer(self):
        if self.visualize:
            from visualizers.price_chart.open_interest import OpenInterestVisualizer
            return OpenInterestVisualizer(self.model)
        return None

    def reset(self):
        self.model.content.clear()

    def process_message(self, msg: OpenInterestMessage):
        self.model.content.append(
            OscillatorRecord(
                time=msg.time,
                value=msg.open_interest
            )
        )