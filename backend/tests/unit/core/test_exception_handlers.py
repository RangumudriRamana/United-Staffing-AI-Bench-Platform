import pytest
from fastapi import Request
from starlette.exceptions import HTTPException

from app.core.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from fastapi.exceptions import RequestValidationError


@pytest.mark.asyncio
async def test_unhandled_exception_handler_returns_500():
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
            "scheme": "http",
        }
    )

    response = await unhandled_exception_handler(
        request,
        Exception("unexpected error"),
    )

    assert response.status_code == 500
    assert response.body == b'{"success":false,"message":"Internal Server Error"}'