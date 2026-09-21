from decimal import Decimal

from app.consultants.enums import MarketingStatus, RateType, VisaStatus
from app.consultants.schemas import (
    AdvancedSearchCriteria,
    ConsultantBase,
    ConsultantFilterParams,
    ConsultantMarketingHistoryResponse,
    ConsultantStatusTransitionRequest,
    UpdateConsultantRequest,
)


def make_base_payload():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "  JOHN.DOE@EXAMPLE.COM  ",
        "phone": "+1 (555) 123-4567",
        "visa_status": VisaStatus.H1B,
    }


def test_consultant_base_normalizes_email_and_phone():
    payload = ConsultantBase(**make_base_payload())

    assert payload.email == "john.doe@example.com"
    assert payload.phone == "15551234567"


def test_consultant_base_allows_none_phone():
    payload = ConsultantBase(
        **{
            **make_base_payload(),
            "phone": None,
        }
    )

    assert payload.phone is None


def test_consultant_base_normalizes_non_string_email_unchanged():
    value = 12345

    result = ConsultantBase.normalize_email(value)

    assert result == value


def test_consultant_base_normalizes_non_string_phone_unchanged():
    value = 123456789

    result = ConsultantBase.normalize_phone(value)

    assert result == value


def test_update_consultant_normalizes_email_and_phone():
    payload = UpdateConsultantRequest(
        email="  UPDATED@EXAMPLE.COM  ",
        phone="+1-800-555-1212",
    )

    assert payload.email == "updated@example.com"
    assert payload.phone == "18005551212"


def test_update_consultant_preserves_none_values():
    payload = UpdateConsultantRequest(
        email=None,
        phone=None,
    )

    assert payload.email is None
    assert payload.phone is None


def test_update_consultant_non_string_validator_inputs():
    email_value = 12345
    phone_value = 987654321

    assert UpdateConsultantRequest.normalize_email(email_value) == email_value
    assert UpdateConsultantRequest.normalize_phone(phone_value) == phone_value


def test_consultant_filter_params_and_advanced_search_defaults():
    filters = ConsultantFilterParams()
    advanced = AdvancedSearchCriteria()

    assert filters.visa_status is None
    assert filters.minimum_experience is None
    assert filters.maximum_rate is None
    assert advanced.technologies == []
    assert advanced.match_mode == "ANY"
    assert advanced.visa_status == []


def test_status_transition_request_and_history_response():
    transition = ConsultantStatusTransitionRequest(
        target_status=MarketingStatus.UNAVAILABLE,
        reason="Ready for submission",
        notes="Updated profile",
    )

    assert transition.target_status == MarketingStatus.UNAVAILABLE
    assert transition.reason == "Ready for submission"
    assert transition.notes == "Updated profile"

    history = ConsultantMarketingHistoryResponse(
        public_id=__import__("uuid").uuid4(),
        status=MarketingStatus.UNAVAILABLE,
        effective_from=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
        changed_by=10,
    )

    assert history.changed_by == 10
    assert history.reason is None
    assert history.notes is None