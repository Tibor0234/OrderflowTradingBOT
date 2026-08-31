import inspect

from session_pairs.resource import Resource
from session_pairs.price_chart_resource import PriceChartResource

# Resources
from analyzers.timeframe.analyzer import TimeframeAnalyzer
from analyzers.open_interest.analyzer import OpenInterestAnalyzer
from analyzers.big_trades.analyzer import BigTradesAnalyzer
from analyzers.volume_delta.simple_analyzer import VolumeDeltaAnalyzer
from analyzers.volume_delta.cumulative_analyzer import CVDAnalyzer
from analyzers.volume_profile.analyzer import VolumeProfileAnalyzer
from analyzers.ohlcv_timeframe.analyzer import OHLCVTimeframeAnalyzer, OHLCVPeriod
from analyzers.ohlcv_volume_profile.analyzer import OHLCVVolumeProfileAnalyzer

# Strategies
from strategies.executable.test import TestStrategy

class UserConfig:

    def get_essentials(self):
        strategy = TestStrategy()
        resources = self._build_resources()
        self._resolve_price_chart_slots(resources)
        visualizers = self._setup_resources(resources)

        return strategy, resources, visualizers

    def _build_resources(self) -> dict[str, Resource]:
        return {
            "big_trades": BigTradesAnalyzer(
                length=100,
                top_pct=2.3,
                visualize=True,
            ),

            "tf_1m": TimeframeAnalyzer(
                candle_seconds=60
            ),
            
            

            "tf_5m": TimeframeAnalyzer(
                candle_seconds=300,
                length=50,
            ),
            "cvd_5m": CVDAnalyzer(),
            "vp_5m": VolumeProfileAnalyzer(),

            "oi": OpenInterestAnalyzer(
                aggregation_minutes=5,
                length=50,
                visualize=True,
                chart_slot=1
            ),

            "ohlcv_1d": OHLCVTimeframeAnalyzer(
                OHLCVPeriod.LAST_DAY
            ),
            "ohlcv_1d_vp": OHLCVVolumeProfileAnalyzer(visualize=False),

            "ohlcv_1w": OHLCVTimeframeAnalyzer(
                OHLCVPeriod.LAST_WEEK
            ),
            "ohlcv_1w_vp": OHLCVVolumeProfileAnalyzer(),
        }

    @staticmethod
    def _resolve_price_chart_slots(resources: dict[str, Resource]):
        timeframes = [
            resource
            for resource in resources.values()
            if isinstance(resource, TimeframeAnalyzer)
        ]
        if len(timeframes) > 2:
            raise ValueError("At most two TimeframeAnalyzer resources can be declared")

        for slot, timeframe in enumerate(timeframes):
            timeframe.resolve_chart_slot(slot)

        for resource in resources.values():
            if isinstance(resource, PriceChartResource) and not isinstance(resource, TimeframeAnalyzer):
                resource.resolve_chart_slot(0)

    def _setup_resources(self, resources: dict[str, Resource]) -> list:
        visualizers = []
        resource_list = list(resources.values())

        for index, current in enumerate(resource_list):
            self._subscribe_to_source(current, resource_list[:index])

            if hasattr(current, "visualizer") and current.visualizer is not None:
                visualizers.append(current.visualizer)

        return visualizers

    def _subscribe_to_source(self, current: Resource, previous_resources: list[Resource]):
        for previous in reversed(previous_resources):
            if not hasattr(previous, "subscribe"):
                continue

            parameters = list(inspect.signature(previous.subscribe).parameters.values())
            expected_type = parameters[0].annotation

            if expected_type is not inspect._empty and issubclass(type(current), expected_type):
                previous.subscribe(current)
                return
