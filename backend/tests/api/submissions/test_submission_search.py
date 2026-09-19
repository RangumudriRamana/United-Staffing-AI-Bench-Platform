from datetime import datetime, timezone
from sqlalchemy.dialects import postgresql

from app.submissions.enums import EmploymentType, SubmissionStatus
from app.submissions.schemas import SubmissionSearchFilters
from app.submissions.search import build_submission_search_pipeline


def compile_query(criteria):
    query = build_submission_search_pipeline(criteria)
    return str(
        query.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_empty_criteria():
    query = compile_query(SubmissionSearchFilters())

    assert "FROM submissions" in query
    assert "deleted_at IS NULL" in query


def test_consultant_filter():
    query = compile_query(
        SubmissionSearchFilters(consultant_id=10)
    )

    assert "submissions.consultant_id = 10" in query


def test_vendor_filter():
    query = compile_query(
        SubmissionSearchFilters(vendor_id=20)
    )

    assert "submissions.vendor_id = 20" in query


def test_client_filter():
    query = compile_query(
        SubmissionSearchFilters(client_id=30)
    )

    assert "submissions.client_id = 30" in query


def test_requirement_filter():
    query = compile_query(
        SubmissionSearchFilters(requirement_id=40)
    )

    assert "submissions.requirement_id = 40" in query


def test_submission_status_filter():
    query = compile_query(
        SubmissionSearchFilters(
            submission_status=SubmissionStatus.SUBMITTED
        )
    )

    assert "submissions.submission_status" in query
    assert "SUBMITTED" in query


def test_employment_type_filter():
    query = compile_query(
        SubmissionSearchFilters(
            employment_type=EmploymentType.C2C
        )
    )

    assert "submissions.employment_type" in query
    assert "C2C" in query

def test_job_title_search():
    query = compile_query(
        SubmissionSearchFilters(job_title="Java")
    )

    assert "JOIN consultants" in query
    assert "submissions.job_title ILIKE '%%Java%%'" in query
    assert "consultants.first_name ILIKE '%%Java%%'" in query
    assert "consultants.last_name ILIKE '%%Java%%'" in query
    assert "consultants.email ILIKE '%%Java%%'" in query


def test_combined_filters():
    query = compile_query(
        SubmissionSearchFilters(
            consultant_id=10,
            vendor_id=20,
            client_id=30,
            requirement_id=40,
            submission_status=SubmissionStatus.SUBMITTED,
            employment_type=EmploymentType.C2C,
            job_title="Python",
        )
    )

    assert "submissions.consultant_id = 10" in query
    assert "submissions.vendor_id = 20" in query
    assert "submissions.client_id = 30" in query
    assert "submissions.requirement_id = 40" in query
    assert "submissions.submission_status" in query
    assert "submissions.employment_type" in query
    assert "submissions.job_title ILIKE '%%Python%%'" in query
