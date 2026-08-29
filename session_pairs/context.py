from session_pairs.resource import Resource
from session_pairs.utils import InstrumentMetadata
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType

class SessionPairContext:
    def __init__(self):
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_START, self.start_new_session_pair)
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_METADATA, self.set_instrument_metadata)

        self.resources: dict[str, Resource] = {}
        self.instrument_metadata: InstrumentMetadata | None = None

    def set_resources(self, resources: dict[str, Resource]):
        self.resources = resources
        return self

    def start_new_session_pair(self):
        for resource in self.resources.values():
            resource.reset()

    def set_instrument_metadata(self, instrument_metadata=None):
        self.instrument_metadata = instrument_metadata

    def get_resource(self, name: str):
        resource = self.resources.get(name, None)
        return resource.model if resource else None

    def get_instrument_metadata(self) -> InstrumentMetadata | None:
        return self.instrument_metadata