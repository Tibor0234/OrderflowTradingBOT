import inspect

#Resources
from analyzers.timeframe.analyzer import TimeframeAnalyzer
from analyzers.open_interest.analyzer import OpenInterestAnalyzer
from analyzers.volume_delta.simple_analyzer import VolumeDeltaAnalyzer
from analyzers.volume_delta.cumulative_analyzer import CVDAnalyzer
from analyzers.volume_profile.analyzer import VolumeProfileAnalyzer
from analyzers.context_timeframe.analyzer import ContextTimeframeAnalyzer, ContextPeriod
from analyzers.context_volume_profile.analyzer import ContextVolumeProfileAnalyzer

#Strategies
from strategies.executable.test import TestStrategy

def setup_resources(resources: dict):
    resource_list = list(resources.values())
    visualizers = []

    for i, current in enumerate(resource_list):

        for prev in reversed(resource_list[:i]):
            if hasattr(prev, "subscribe"):
                sig = inspect.signature(prev.subscribe)
                params = list(sig.parameters.values())

                expected = params[0].annotation

                if expected is not inspect._empty:
                    if issubclass(type(current), expected):
                        prev.subscribe(current)
                        break

        if hasattr(current, "visualizer") and current.visualizer is not None:
            visualizers.append(current.visualizer)

    return visualizers

# --------------------------
# ------ USER CONFIG -------
# --------------------------

def get_essentials():
    # 🚨 Starting balance (USD)
    starting_balance = 100_000

    # ⚡ Strategy
    strategy = TestStrategy()

    # 🛠 Resources
    resources = {
        'tf_1m': TimeframeAnalyzer(candle_seconds=60),
        'cvd_1m': CVDAnalyzer(visualize=True),
        'vp_1m': VolumeProfileAnalyzer(),

        'oi': OpenInterestAnalyzer(visualize=False),

        'ctx_1d': ContextTimeframeAnalyzer(ContextPeriod.LAST_DAY),
        #'ctx_1d_vp': ContextVolumeProfileAnalyzer(),

        'ctx_1w': ContextTimeframeAnalyzer(ContextPeriod.LAST_WEEK),
        #'ctx_1w_vp': ContextVolumeProfileAnalyzer(),
    }

    visualizers = setup_resources(resources)

    return starting_balance, strategy, resources, visualizers