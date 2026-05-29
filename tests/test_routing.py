import pytest
from dz_routing_engine import DZRoutingEngine, DZNode, RouteMetric

def test_routing_engine():
    engine = DZRoutingEngine()
    engine.add_node(DZNode("A", "loc", 100, {"B": 10}, {"B": 1}, 1.0, 10))
    engine.add_node(DZNode("B", "loc", 100, {"A": 10}, {"A": 1}, 1.0, 10))
    route = engine.find_route("A", "B", RouteMetric.LATENCY)
    assert route.path == ["A", "B"]
