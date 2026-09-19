from sqlalchemy.dialects import postgresql

from app.requirements.enums import RequirementPriority, RequirementStatus, WorkModel
from app.requirements.schemas import RequirementSearchCriteria
from app.requirements.search import build_requirement_search_pipeline
from app.submissions.enums import EmploymentType


def compile_query(criteria):
    query = build_requirement_search_pipeline(criteria)
    return str(
        query.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_empty_criteria():
    query = compile_query(RequirementSearchCriteria())

    assert "FROM requirements" in query
    assert "WHERE" not in query


def test_vendor_filter():
    query = compile_query(
        RequirementSearchCriteria(vendor_id=10)
    )

    assert "requirements.vendor_id = 10" in query


def test_client_filter():
    query = compile_query(
        RequirementSearchCriteria(client_id=20)
    )

    assert "requirements.client_id = 20" in query


def test_owner_recruiter_filter():
    query = compile_query(
        RequirementSearchCriteria(owner_recruiter_id=30)
    )

    assert "requirements.owner_recruiter_id = 30" in query


def test_status_filter():
    query = compile_query(
        RequirementSearchCriteria(status=RequirementStatus.OPEN)
    )

    assert "requirements.status" in query
    assert "OPEN" in query


def test_employment_type_filter():
    query = compile_query(
        RequirementSearchCriteria(employment_type=EmploymentType.C2C)
    )

    assert "requirements.employment_type" in query
    assert "C2C" in query


def test_work_model_filter():
    query = compile_query(
        RequirementSearchCriteria(work_model=WorkModel.REMOTE)
    )

    assert "requirements.work_model" in query
    assert "REMOTE" in query


def test_priority_filter():
    query = compile_query(
        RequirementSearchCriteria(priority=RequirementPriority.HIGH)
    )

    assert "requirements.priority" in query
    assert "HIGH" in query


def test_text_search():
    query = compile_query(
        RequirementSearchCriteria(search="Java")
    )

    assert "ILIKE '%%Java%%'" in query
    assert "requirements.job_title" in query
    assert "requirements.job_code" in query
    assert "requirements.description" in query
    assert "requirements.location" in query


def test_text_search_trims_whitespace():
    query = compile_query(
        RequirementSearchCriteria(search="  Java  ")
    )

    assert "ILIKE '%%Java%%'" in query


def test_combined_filters():
    query = compile_query(
        RequirementSearchCriteria(
            vendor_id=10,
            client_id=20,
            owner_recruiter_id=30,
            status=RequirementStatus.OPEN,
            employment_type=EmploymentType.C2C,
            work_model=WorkModel.REMOTE,
            priority=RequirementPriority.HIGH,
            search="Python",
        )
    )

    assert query.count(" AND ") == 7
    assert "requirements.vendor_id = 10" in query
    assert "requirements.client_id = 20" in query
    assert "requirements.owner_recruiter_id = 30" in query
    assert "requirements.status" in query
    assert "requirements.employment_type" in query
    assert "requirements.work_model" in query
    assert "requirements.priority" in query
    assert "ILIKE '%%Python%%'" in query
