import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database.session import get_db

# Explicitly import fixtures to make them globally accessible across all suite test files
from tests.fixtures.database import db_session, prepare_database
from tests.fixtures.users import sample_user, sample_admin
from tests.fixtures.auth import user_headers, admin_headers


@pytest_asyncio.fixture
async def client(db_session):
    """
    Configures and yields a fully operational ASGI test engine client.
    Overrides the main database injection token with our function-scoped transaction session.
    """
    # Instruct the runtime dependency map to bypass production session initialization
    app.dependency_overrides[get_db] = lambda: db_session
    
    # Modern HTTPX uses ASGITransport to route requests directly to the FastAPI app instance
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client
        
    # Clean up the overriding logic completely to avoid cross-contamination
    app.dependency_overrides.clear()