class EventBus:
    _instance = None

    listeners: dict

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.listeners = {}
        return cls._instance

    def subscribe(self, event_type, handler):
        """Feliratkoztat egy metódust az event-re."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(handler)

    def emit(self, event_type, *args, **kwargs):
        """Az összes feliratkozott handler meghívása tetszőleges paraméterekkel."""
        for handler in self.listeners.get(event_type, []):
            handler(*args, **kwargs)