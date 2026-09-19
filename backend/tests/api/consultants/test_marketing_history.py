import pytest
from app.main import app

from app.consultants.enums import MarketingStatus
from app.consultants.schemas import ConsultantCreateRequest
from app.consultants.service import ConsultantService


@pytest.mark.asyncio
class TestConsultantMarketingHistoryAPI:

    async def test_get_marketing_history_returns_lifecycle_records(
        self,
        client,
        db_session,
        sample_admin,
        admin_headers,
    ):
        # Arrange
        consultant_payload = ConsultantCreateRequest(
            first_name="History",
            last_name="Test",
            email="history.test@unitedstaffing.ai",
            phone="9999999998",
            current_title="Senior Java Developer",
            total_experience_years=5,
            current_location="Hyderabad",
            preferred_location="Remote",
            relocation_available=False,
            remote_preference="Remote",
            visa_status="H1B",
            visa_expiration="2027-12-31",
            work_authorized=True,
            availability_date="2026-09-07",
            marketing_status=MarketingStatus.NEW,
            expected_rate=70,
        )

        service = ConsultantService(db_session)

        consultant = await service.create_consultant(
            consultant_payload,
            current_user_id=sample_admin.id,
        )

        # Act
        await service.transition_marketing_status(
            public_id=consultant.public_id,
            new_status=MarketingStatus.READY_FOR_MARKETING,
            changed_by_user_id=sample_admin.id,
            reason="Test preparation",
            notes="Test transition to ready state.",
        )

        await service.transition_marketing_status(
            public_id=consultant.public_id,
            new_status=MarketingStatus.MARKETING_ACTIVE,
            changed_by_user_id=sample_admin.id,
            reason="Test marketing start",
            notes="Test transition to active marketing.",
        )

        direct_history = await service.get_marketing_history(
            consultant.public_id
        )

        print("DIRECT HISTORY COUNT:", len(direct_history))
        print(
            "DIRECT HISTORY STATUSES:",
            [record.status.value for record in direct_history]
        )

        from fastapi.routing import APIRoute

        for route in app.routes:
            if isinstance(route, APIRoute):
                print(
                    "ROUTE:",
                    route.path,
                    "| METHODS:",
                    route.methods,
                    "| ENDPOINT:",
                    route.endpoint.__name__,
                )

        response = await client.get(
            f"/api/v1/consultants/{consultant.public_id}/marketing/history",
            headers=admin_headers,
        )

        # Assert
        assert response.status_code == 200


        response_json = response.json()

        assert isinstance(response_json, list)
        assert len(response_json) == 3

        assert response_json[0]["status"] == "MARKETING_ACTIVE"
        assert response_json[1]["status"] == "READY_FOR_MARKETING"
        assert response_json[2]["status"] == "NEW"

        assert response_json[0]["effective_until"] is None
        assert response_json[1]["effective_until"] is not None
        assert response_json[2]["effective_until"] is not None

        assert response_json[0]["changed_by"] == sample_admin.id
        assert response_json[0]["reason"] == "Test marketing start"
        assert response_json[0]["notes"] == "Test transition to active marketing."
