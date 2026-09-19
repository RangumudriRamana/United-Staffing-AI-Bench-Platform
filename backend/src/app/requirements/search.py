from sqlalchemy import Select, or_, select

from app.requirements.models import Requirement
from app.requirements.schemas import RequirementSearchCriteria


def build_requirement_search_pipeline(
    criteria: RequirementSearchCriteria,
) -> Select:
    """Build requirement search query."""

    query = select(Requirement)

    if criteria.vendor_id is not None:
        query = query.where(
            Requirement.vendor_id == criteria.vendor_id
        )

    if criteria.client_id is not None:
        query = query.where(
            Requirement.client_id == criteria.client_id
        )

    if criteria.owner_recruiter_id is not None:
        query = query.where(
            Requirement.owner_recruiter_id == criteria.owner_recruiter_id
        )

    if criteria.status is not None:
        query = query.where(
            Requirement.status == criteria.status
        )

    if criteria.employment_type is not None:
        query = query.where(
            Requirement.employment_type == criteria.employment_type
        )

    if criteria.work_model is not None:
        query = query.where(
            Requirement.work_model == criteria.work_model
        )

    if criteria.priority is not None:
        query = query.where(
            Requirement.priority == criteria.priority
        )

    if criteria.search:
        token = f"%{criteria.search.strip()}%"

        query = query.where(
            or_(
                Requirement.job_title.ilike(token),
                Requirement.job_code.ilike(token),
                Requirement.description.ilike(token),
                Requirement.location.ilike(token),
            )
        )

    return query