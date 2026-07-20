from sqlalchemy import select, or_, Select
from app.submissions.models import Submission
from app.consultants.models import Consultant
from app.submissions.schemas import SubmissionSearchCriteria

def build_submission_search_pipeline(criteria: SubmissionSearchCriteria) -> Select:
    """
    Assembles a highly optimized, composable sequence of filters targeting
    submission boundaries. Completely decoupled from execution contexts.
    """
    # 1. Base query selection protecting soft delete boundaries
    query = select(Submission).where(Submission.deleted_at == None)

    # 2. Apply structured primary foreign key boundaries
    if criteria.consultant_id is not None:
        query = query.where(Submission.consultant_id == criteria.consultant_id)
        
    if criteria.recruiter_id is not None:
        query = query.where(Submission.submitted_by == criteria.recruiter_id)

    # 3. Apply exact/partial structural metadata filters
    if criteria.submission_status:
        query = query.where(Submission.submission_status == criteria.submission_status)
        
    if criteria.client_name:
        query = query.where(Submission.client_name.ilike(f"%{criteria.client_name}%"))

    # 4. Enforce strict operational date ranges
    if criteria.date_from:
        query = query.where(Submission.submitted_at >= criteria.date_from)
    if criteria.date_to:
        query = query.where(Submission.submitted_at <= criteria.date_to)

    # 5. Execute unified multi-entity global text box tracking
    if criteria.search_text:
        search_token = f"%{criteria.search_text}%"
        
        # Join the parent consultant model to safely query identity records
        query = query.join(Consultant).where(
            or_(
                Submission.client_name.ilike(search_token),
                Submission.job_title.ilike(search_token),
                Consultant.first_name.ilike(search_token),
                Consultant.last_name.ilike(search_token),
                Consultant.email.ilike(search_token)
            )
        )

    return query