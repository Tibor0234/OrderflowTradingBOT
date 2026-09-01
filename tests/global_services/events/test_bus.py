from global_services.events.bus import EventBus


def test_emit_calls_each_handler_with_event_arguments():
    received = []
    event_bus = EventBus()
    event_bus.subscribe("trade", lambda price, quantity: received.append((price, quantity)))

    event_bus.emit("trade", 100, quantity=2)

    assert received == [(100, 2)]