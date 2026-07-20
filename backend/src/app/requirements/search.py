from sqlalchemy import select, or_, Select
from app.requirements.models import Requirement
from app.requirements.schemas import RequirementSearchCriteria

def build_requirement_search_pipeline(criteria: RequirementSearchCriteria) -> Select:
    """Assembles decoupled database filtering sequences completely isolated from side effects."""
    query = select(Requirement)

    # Apply relational foreign mappings
    if criteria.vendor_id is not None:
        query = query.where(Requirement.vendor_id == criteria.vendor_id)
    if criteria.client_id is not None:
        query = query.where(Requirement.client_id == criteria.client_id)
    if criteria.owner_recruiter_id is not None:
        query = query.where(Requirement.owner_recruiter_id == criteria.owner_recruiter_id)

    # Apply status and operational metrics
    if criteria.status:
        query = query.where(Requirement.status == criteria.status)
    if criteria.priority:
        query = query.where(Requirement.priority == criteria.priority)

    # Apply numeric bounds checking
    if criteria.experience_min is not None:
        query = query.where(Requirement.experience_min >= criteria.experience_min)
    if criteria.experience_max is not None:
        query = query.where(Requirement.experience_max <= criteria.experience_max)

    # Apply global cross-field fuzzy lookups
    if criteria.search_text:
        token = f"%{criteria.search_text}%"
        query = query.where(
            or_(
                Requirement.job_title.ilike(token),
                Requirement.job_code.ilike(token),
                Requirement.description.ilike(token)
            )
        )

    return query