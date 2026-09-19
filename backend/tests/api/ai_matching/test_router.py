import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import UUID

from app.ai_matching.router import (
    batch_match,
    get_history,
    match,
)
from app.ai_matching.schemas import (
    BatchMatchRequest,
    BatchMatchResponse,
    MatchHistoryResponse,
)


@pytest.mark.asyncio
async def test_match_endpoint_delegates_to_service():
    request = BatchMatchRequest(
        requirement_id=UUID(
            "11111111-1111-1111-1111-111111111111"
        )
    )

    response = BatchMatchResponse(matches=[])

    service = SimpleNamespace(
        match=AsyncMock(return_value=response)
    )

    with patch(
        "app.ai_matching.router.AIMatchingService",
        return_value=service,
    ):
        result = await match(request, SimpleNamespace())

    assert result == response
    service.match.assert_awaited_once_with(request)


@pytest.mark.asyncio
async def test_get_history_endpoint_delegates_to_service():
    response = MatchHistoryResponse(history=[])

    service = SimpleNamespace(
        get_history=AsyncMock(return_value=response)
    )

    with patch(
        "app.ai_matching.router.AIMatchingService",
        return_value=service,
    ):
        result = await get_history(SimpleNamespace())

    assert result == response
    service.get_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_batch_match_endpoint_delegates_to_service():
    request = BatchMatchRequest(
        requirement_id=UUID(
            "11111111-1111-1111-1111-111111111111"
        )
    )

    response = BatchMatchResponse(matches=[])

    service = SimpleNamespace(
        batch_match=AsyncMock(return_value=response)
    )

    with patch(
        "app.ai_matching.router.AIMatchingService",
        return_value=service,
    ):
        result = await batch_match(
            request,
            SimpleNamespace(),
        )

    assert result == response
    service.batch_match.assert_awaited_once_with(request)