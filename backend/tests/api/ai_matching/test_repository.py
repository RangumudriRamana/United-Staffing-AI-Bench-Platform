import pytest
from sqlalchemy import select

from app.ai_matching.models import AIMatchHistory
from app.ai_matching.repository import AIMatchingRepository
from app.consultants.models import Consultant
from app.requirements.models import Requirement
from tests.factories.user_factory import UserFactory
from tests.fixtures.database import db_session


@pytest.mark.asyncio
async def test_get_consultant(db_session):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()

    consultant = Consultant(
        first_name="John",
        last_name="Doe",
        email="john.ai.repository@test.com",
        total_experience_years=5,
        current_location="Dallas, TX",
        visa_status="H1B",
        recruiter_id=user.id,
        created_by=user.id,
    )
    db_session.add(consultant)
    await db_session.flush()

    repo = AIMatchingRepository(db_session)

    result = await repo.get_consultant(consultant.public_id)

    assert result is not None
    assert result.id == consultant.id
    assert result.public_id == consultant.public_id
    assert result.technologies == []


@pytest.mark.asyncio
async def test_get_consultant_not_found(db_session):
    from uuid import uuid4

    repo = AIMatchingRepository(db_session)

    result = await repo.get_consultant(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_requirement(db_session):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()

    from tests.factories.vendors import VendorFactory, ClientFactory

    vendor = VendorFactory.build(created_by=user.id)
    db_session.add(vendor)
    await db_session.flush()

    client = ClientFactory.build(vendor_id=vendor.id, created_by=user.id)
    db_session.add(client)
    await db_session.flush()

    requirement = Requirement(
        vendor_id=vendor.id,
        client_id=client.id,
        owner_recruiter_id=user.id,
        job_title="AI Repository Test",
        job_code="AI-REPO-001",
        experience_min=3,
        location="Dallas, TX",
    )
    db_session.add(requirement)
    await db_session.flush()

    repo = AIMatchingRepository(db_session)

    result = await repo.get_requirement(requirement.public_id)

    assert result is not None
    assert result.id == requirement.id
    assert result.public_id == requirement.public_id
    assert result.technologies == []


@pytest.mark.asyncio
async def test_get_requirement_not_found(db_session):
    from uuid import uuid4

    repo = AIMatchingRepository(db_session)

    result = await repo.get_requirement(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_all_consultants(db_session):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()

    consultant1 = Consultant(
        first_name="John",
        last_name="One",
        email="john.ai.all.1@test.com",
        total_experience_years=5,
        current_location="Dallas, TX",
        visa_status="H1B",
        recruiter_id=user.id,
        created_by=user.id,
    )

    consultant2 = Consultant(
        first_name="Jane",
        last_name="Two",
        email="jane.ai.all.2@test.com",
        total_experience_years=4,
        current_location="Austin, TX",
        visa_status="H1B",
        recruiter_id=user.id,
        created_by=user.id,
    )

    db_session.add_all([consultant1, consultant2])
    await db_session.flush()

    repo = AIMatchingRepository(db_session)

    result = await repo.get_all_consultants()

    ids = {consultant.id for consultant in result}

    assert consultant1.id in ids
    assert consultant2.id in ids
    assert len(result) == 2


@pytest.mark.asyncio
async def test_create_match_history(db_session):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()

    from tests.factories.vendors import VendorFactory, ClientFactory

    vendor = VendorFactory.build(created_by=user.id)
    db_session.add(vendor)
    await db_session.flush()

    client = ClientFactory.build(vendor_id=vendor.id, created_by=user.id)
    db_session.add(client)
    await db_session.flush()

    requirement = Requirement(
        vendor_id=vendor.id,
        client_id=client.id,
        owner_recruiter_id=user.id,
        job_title="History Test",
        job_code="AI-HISTORY-001",
        experience_min=3,
    )
    consultant = Consultant(
        first_name="History",
        last_name="Consultant",
        email="history.ai@test.com",
        total_experience_years=5,
        visa_status="H1B",
        recruiter_id=user.id,
        created_by=user.id,
    )

    db_session.add_all([requirement, consultant])
    await db_session.flush()

    repo = AIMatchingRepository(db_session)

    history = await repo.create_match_history(
        consultant_id=consultant.id,
        requirement_id=requirement.id,
        match_score=87.5,
        recommendation="Excellent Match",
    )

    assert history.id is not None
    assert history.consultant_id == consultant.id
    assert history.requirement_id == requirement.id
    assert history.match_score == 87.5
    assert history.recommendation == "Excellent Match"


@pytest.mark.asyncio
async def test_get_match_history(db_session):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()

    from tests.factories.vendors import VendorFactory, ClientFactory

    vendor = VendorFactory.build(created_by=user.id)
    db_session.add(vendor)
    await db_session.flush()

    client = ClientFactory.build(vendor_id=vendor.id, created_by=user.id)
    db_session.add(client)
    await db_session.flush()

    requirement = Requirement(
        vendor_id=vendor.id,
        client_id=client.id,
        owner_recruiter_id=user.id,
        job_title="History Lookup",
        job_code="AI-HISTORY-LOOKUP-001",
        experience_min=3,
    )
    consultant = Consultant(
        first_name="Lookup",
        last_name="Consultant",
        email="lookup.ai@test.com",
        total_experience_years=5,
        visa_status="H1B",
        recruiter_id=user.id,
        created_by=user.id,
    )

    db_session.add_all([requirement, consultant])
    await db_session.flush()

    repo = AIMatchingRepository(db_session)

    await repo.create_match_history(
        consultant_id=consultant.id,
        requirement_id=requirement.id,
        match_score=75.0,
        recommendation="Good Match",
    )
    await db_session.commit()

    result = await repo.get_match_history()

    assert len(result) == 1
    assert result[0].consultant.id == consultant.id
    assert result[0].requirement.id == requirement.id
    assert result[0].match_score == 75.0
    assert result[0].recommendation == "Good Match"
