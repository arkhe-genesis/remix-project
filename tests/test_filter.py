import pytest
from edge_filter_controller import EdgeFilterController, FilterAction

def test_edge_filter():
    controller = EdgeFilterController()
    packet = {
        "packet_id": "test1",
        "source_substrate": "923",
        "payload": b"hello",
        "timestamp_ns": 1234567890,
        "seal": "3338be694f50c5f338814986cdf0686453a888b84f424d792af4b9202398f392"
    }
    result = controller.filter_packet(packet)
    assert result.action == FilterAction.DROP_TTL_EXPIRED
