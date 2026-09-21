import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.core.middleware import (
    StructuredJSONFormatter,
    TelemetryPerimeterMiddleware,
    correlation_id_ctx,
    user_id_ctx,
)


def make_request(
    path="/test",
    method="GET",
    correlation_id=None,
    user=None,
):
    headers = {}
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [
            (key.lower().encode(), value.encode())
            for key, value in headers.items()
        ],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
    }

    request = Request(scope)

    if user is not None:
        request.state.user = user

    return request


def make_middleware():
    return TelemetryPerimeterMiddleware.__new__(TelemetryPerimeterMiddleware)


@pytest.mark.asyncio
async def test_dispatch_uses_incoming_correlation_id_and_user():
    middleware = make_middleware()

    request = make_request(
        path="/protected",
        method="POST",
        correlation_id="incoming-correlation-id",
        user=SimpleNamespace(id=42),
    )

    response = Response(status_code=201)

    async def call_next(req):
        assert correlation_id_ctx.get() == "incoming-correlation-id"
        assert user_id_ctx.get() == "42"
        return response

    result = await middleware.dispatch(request, call_next)

    assert result is response
    assert result.headers["X-Correlation-ID"] == "incoming-correlation-id"
    assert result.headers["X-Request-ID"]
    assert result.headers["X-Content-Type-Options"] == "nosniff"
    assert result.headers["X-Frame-Options"] == "DENY"
    assert result.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    assert correlation_id_ctx.get() == ""
    assert user_id_ctx.get() == "ANONYMOUS"


@pytest.mark.asyncio
async def test_dispatch_generates_correlation_id_for_missing_header():
    middleware = make_middleware()

    request = make_request()

    response = Response(status_code=200)

    with patch(
        "app.core.middleware.uuid.uuid4",
        side_effect=[
            "generated-correlation-id",
            "generated-request-id",
        ],
    ):
        async def call_next(req):
            assert correlation_id_ctx.get() == "generated-correlation-id"
            assert user_id_ctx.get() == "ANONYMOUS"
            return response

        result = await middleware.dispatch(request, call_next)

    assert result.headers["X-Correlation-ID"] == "generated-correlation-id"
    assert result.headers["X-Request-ID"] == "generated-request-id"
    assert correlation_id_ctx.get() == ""
    assert user_id_ctx.get() == "ANONYMOUS"


@pytest.mark.asyncio
async def test_dispatch_handles_request_state_without_user():
    middleware = make_middleware()

    request = make_request()

    response = Response(status_code=204)

    async def call_next(req):
        assert not hasattr(req.state, "user")
        assert user_id_ctx.get() == "ANONYMOUS"
        return response

    result = await middleware.dispatch(request, call_next)

    assert result.status_code == 204
    assert user_id_ctx.get() == "ANONYMOUS"


@pytest.mark.asyncio
async def test_dispatch_logs_and_reraises_exception():
    middleware = make_middleware()

    request = make_request(path="/failure")

    error = RuntimeError("boom")

    async def call_next(req):
        raise error

    logger = MagicMock()

    with patch(
        "app.core.middleware.logging.getLogger",
        return_value=logger,
    ):
        with pytest.raises(RuntimeError, match="boom"):
            await middleware.dispatch(request, call_next)

    assert logger.info.call_count == 1
    logger.error.assert_called_once()

    error_message = logger.error.call_args.args[0]
    assert "Unhandled Exception Caught at Perimeter Boundary" in error_message
    assert "boom" in error_message

    assert correlation_id_ctx.get() == ""
    assert user_id_ctx.get() == "ANONYMOUS"


def test_structured_json_formatter_formats_basic_record():
    formatter = StructuredJSONFormatter()

    correlation_token = correlation_id_ctx.set("corr-123")
    user_token = user_id_ctx.set("user-456")

    try:
        record = logging.LogRecord(
            name="app.telemetry",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        payload = json.loads(output)

        assert payload["level"] == "INFO"
        assert payload["service"] == "bench-sales-engine"
        assert payload["module"] == "test_middleware"
        assert payload["message"] == "Test message"
        assert payload["correlation_id"] == "corr-123"
        assert payload["user_id"] == "user-456"
        assert "timestamp" in payload
        assert "exception" not in payload
    finally:
        correlation_id_ctx.reset(correlation_token)
        user_id_ctx.reset(user_token)


def test_structured_json_formatter_includes_exception():
    formatter = StructuredJSONFormatter()

    try:
        raise ValueError("formatter failure")
    except ValueError:
        record = logging.LogRecord(
            name="app.telemetry",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Failure",
            args=(),
            exc_info=__import__("sys").exc_info(),
        )

    output = formatter.format(record)
    payload = json.loads(output)

    assert payload["level"] == "ERROR"
    assert payload["message"] == "Failure"
    assert "exception" in payload
    assert "ValueError" in payload["exception"]
    assert "formatter failure" in payload["exception"]