import pytest

from global_services.events.bus import EventBus


@pytest.fixture(autouse=True)
def reset_event_bus():
    EventBus().listeners.clear()