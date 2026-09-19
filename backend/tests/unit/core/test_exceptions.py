from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.core.exceptions import AppException, register_exception_handlers


def test_app_exception_defaults():
    exc = AppException("Something went wrong")

    assert exc.message == "Something went wrong"
    assert exc.error_code == "APPLICATION_ERROR"
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert str(exc) == "Something went wrong"


def test_app_exception_custom_values():
    exc = AppException(
        message="Resource not found",
        error_code="RESOURCE_NOT_FOUND",
        status_code=status.HTTP_404_NOT_FOUND,
    )

    assert exc.message == "Resource not found"
    assert exc.error_code == "RESOURCE_NOT_FOUND"
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc) == "Resource not found"


def test_app_exception_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/app-error")
    async def app_error():
        raise AppException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    client = TestClient(app)

    response = client.get("/app-error")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "success": False,
        "message": "Test error",
        "error_code": "TEST_ERROR",
    }


def test_unhandled_exception_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/unexpected-error")
    async def unexpected_error():
        raise RuntimeError("Unexpected failure")

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get("/unexpected-error")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "success": False,
        "message": "An unexpected error occurred.",
        "error_code": "INTERNAL_SERVER_ERROR",
    }