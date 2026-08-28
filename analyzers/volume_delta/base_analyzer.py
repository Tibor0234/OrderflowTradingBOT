from sessions.resource import Resource
from analyzers.timeframe.analyzer import TimeframeSubscriber
from analyzers.big_trades.analyzer import BigTradesAnalyzer
from analyzers.volume_delta.model import VolumeDelta
from data_managers.trade.utils import TradeMessage
from analyzers.utils import OscillatorRecord

class BaseVolumeDeltaAnalyzer(Resource, TimeframeSubscriber):
    def __init__(self, big_trades: BigTradesAnalyzer | None = None, visualize=True):
        self.name: str
        self.visualize = visualize
        self.big_trades_analyzer = big_trades

        self.new_starting_value = None

    @property
    def visualizer(self):
        if self.visualize:
            return self.get_visualizer()
        return None

    def init_model(self, length):
        self.model: VolumeDelta = VolumeDelta(length)

    def reset(self):
        self.model.history.clear()
        self.model.current = None
        self.new_starting_value = None

    def on_timeframe_update(self, msg: TradeMessage):
        if self.model.current is None:
            self.model.current = OscillatorRecord(
                time=msg.time,
                value=self.new_starting_value if self.new_starting_value is not None else 0
            )

        if self.big_trades_analyzer is not None:
            if not self.big_trades_analyzer.is_big_trade(msg.quantity):
                return

        delta = msg.quantity * msg.side.value
        self.model.current.value += delta

    def on_candle_close(self, next_time: int | None = None):
        if self.model.current is not None:
            self.model.history.append(self.model.current)

        self.model.current = self.new_current_record(next_time)

    def get_visualizer(self):
        raise NotImplementedError("get_visualizer must be implemented")
    
    def new_current_record(self, next_time: int | None = None):
        raise NotImplementedError("new_current_record must be implemented")