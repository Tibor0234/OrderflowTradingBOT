from sessions.resource import Resource
from sessions.utils import InstrumentMetadata
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType

class SessionContext:
    def __init__(self):
        EventBus().subscribe(EventBusMsgType.SESSION_START, self.start_new_session)

        self.resources: dict[str, Resource] = {}
        self.instrument_metadata: InstrumentMetadata | None = None

    def set_resources(self, resources: dict[str, Resource]):
        self.resources = resources
        return self

    def start_new_session(self, instrument_metadata=None):
        for resource in self.resources.values():
            resource.reset()
        self.instrument_metadata = instrument_metadata

    def get_resource(self, name: str):
        resource = self.resources.get(name, None)
        return resource.model if resource else None

    def get_instrument_metadata(self) -> InstrumentMetadata | None:
        return self.instrument_metadata