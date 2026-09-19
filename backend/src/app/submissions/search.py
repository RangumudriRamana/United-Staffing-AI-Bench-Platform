from sqlalchemy import select, or_, Select
from app.submissions.models import Submission
from app.consultants.models import Consultant
from app.submissions.schemas import SubmissionSearchFilters


def build_submission_search_pipeline(
    criteria: SubmissionSearchFilters,
) -> Select:
    """
    Assembles a composable query for submission filtering.
    """

    query = select(Submission).where(Submission.deleted_at.is_(None))

    # Foreign key filters
    if criteria.consultant_id is not None:
        query = query.where(
            Submission.consultant_id == criteria.consultant_id
        )

    if criteria.vendor_id is not None:
        query = query.where(
            Submission.vendor_id == criteria.vendor_id
        )

    if criteria.client_id is not None:
        query = query.where(
            Submission.client_id == criteria.client_id
        )

    if criteria.requirement_id is not None:
        query = query.where(
            Submission.requirement_id == criteria.requirement_id
        )

    # Enum filters
    if criteria.submission_status:
        query = query.where(
            Submission.submission_status == criteria.submission_status
        )

    if criteria.employment_type:
        query = query.where(
            Submission.employment_type == criteria.employment_type
        )

    # Job title search
    if criteria.job_title:
        token = f"%{criteria.job_title}%"

        query = query.join(
            Consultant,
            Submission.consultant_id == Consultant.id,
        ).where(
            or_(
                Submission.job_title.ilike(token),
                Consultant.first_name.ilike(token),
                Consultant.last_name.ilike(token),
                Consultant.email.ilike(token),
            )
        )

    return query