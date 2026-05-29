import pytest
from doublezero_bridge import DoubleZeroBridge, DZNodeType, DZPriority, DZPacket

@pytest.mark.asyncio
async def test_dz_bridge_init():
    bridge = DoubleZeroBridge(node_type=DZNodeType.USER)
    assert bridge.node_type == DZNodeType.USER
