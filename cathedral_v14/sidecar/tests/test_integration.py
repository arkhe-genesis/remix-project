import asyncio
import pytest
from unittest.mock import patch, MagicMock

import aiohttp
from aiohttp import web

from sidecar.client import GgufSidecarClient

async def handler_success(request):
    return web.json_response({"text": "Hello world", "tokens": 5, "cache_hit": False})

async def handler_slow(request):
    await asyncio.sleep(0.5)
    return web.json_response({"text": "Slow response", "tokens": 5, "cache_hit": False})

async def handler_error(request):
    return web.Response(status=500, text="Internal Server Error")

@pytest.fixture
def success_server_app():
    app = web.Application()
    app.router.add_post('/v1/generate', handler_success)
    return app

@pytest.fixture
def error_server_app():
    app = web.Application()
    app.router.add_post('/v1/generate', handler_error)
    return app

@pytest.fixture
def recovery_server_app():
    app = web.Application()

    call_count = 0
    async def handler_recovery(request):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return web.Response(status=500, text="Internal Server Error")
        return web.json_response({"text": "Recovered", "tokens": 5, "cache_hit": False})

    app.router.add_post('/v1/generate', handler_recovery)
    return app

@pytest.mark.asyncio
async def test_circuit_breaker_success(aiohttp_server, success_server_app):
    server = await aiohttp_server(success_server_app)
    config = {
        "sidecar_url": f"http://{server.host}:{server.port}",
        "sidecar_token": "cathedral-super-secret-token",
    }
    client = GgufSidecarClient(config)

    resp = await client.generate("test prompt")
    assert resp["text"] == "Hello world"
    assert client.circuit._state == "CLOSED"

    await client.close()

@pytest.mark.asyncio
async def test_circuit_breaker_open_and_fallback(aiohttp_server, error_server_app):
    server = await aiohttp_server(error_server_app)
    config = {
        "sidecar_url": f"http://{server.host}:{server.port}",
        "sidecar_token": "cathedral-super-secret-token",
        "circuit_max_failures": 2,
    }
    client = GgufSidecarClient(config)

    # We need 2 fully failed generate calls to open the circuit
    # because record_failure is called once per generate call
    resp1 = await client.generate("test prompt 1", max_retries=0)
    assert "FALLBACK" in resp1["text"]
    assert client.circuit._state == "CLOSED"

    resp2 = await client.generate("test prompt 2", max_retries=0)
    assert "FALLBACK" in resp2["text"]
    assert client.circuit._state == "OPEN"

    # Next call should immediately fallback without hitting the network
    resp3 = await client.generate("test prompt 3", max_retries=0)
    assert "FALLBACK" in resp3["text"]

    await client.close()

@pytest.mark.asyncio
async def test_circuit_breaker_recovery(aiohttp_server, recovery_server_app):
    server = await aiohttp_server(recovery_server_app)
    config = {
        "sidecar_url": f"http://{server.host}:{server.port}",
        "sidecar_token": "cathedral-super-secret-token",
        "circuit_max_failures": 2,
        "circuit_recovery_s": 0.1,  # Short recovery for testing
    }
    client = GgufSidecarClient(config)

    # Fail the circuit (needs 2 failures)
    await client.generate("fail 1", max_retries=0)
    await client.generate("fail 2", max_retries=0)

    assert client.circuit._state == "OPEN"

    # Wait for recovery timeout
    await asyncio.sleep(0.2)

    # Next call should be HALF_OPEN and succeed because call_count is now > 2
    resp = await client.generate("recover")
    assert resp["text"] == "Recovered"
    assert client.circuit._state == "CLOSED"

    await client.close()
