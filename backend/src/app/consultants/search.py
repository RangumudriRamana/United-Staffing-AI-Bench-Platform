from sqlalchemy import select, func, or_, Select
from app.models.consultant import Consultant
from app.models.consultant_technology import ConsultantTechnology
from app.models.technology import Technology
from app.consultants.schemas import AdvancedSearchCriteria


def build_advanced_search_query(criteria: AdvancedSearchCriteria) -> Select:
    """
    Assembles a composable, high-performance pipeline of criteria transformations.
    Keeps database retrieval strictly isolated from down-stream ranking metrics.
    """
    # 1. Base Query Selection targeting only active profiles
    query = select(Consultant).where(Consultant.deleted_at == None)

    # 2. Inject Structured Technology Array Filters
    if criteria.technologies:
        # Normalize incoming tech strings to ensure clean matches
        cleaned_techs = [t.strip().lower() for t in criteria.technologies]

        if criteria.match_mode == "ALL":
            # ALL Strategy: Consultant must match every single tech requirement item
            subq = (
                select(ConsultantTechnology.consultant_id)
                .join(Technology)
                .where(
                    func.lower(Technology.name).in_(cleaned_techs),
                    ConsultantTechnology.deleted_at == None
                )
                .group_by(ConsultantTechnology.consultant_id)
                .having(func.count(Technology.id) == len(cleaned_techs))
            )
            
            # If a minimum tech-specific experience bound is requested, enforce it inside the match window
            if criteria.min_tech_experience is not None:
                subq = subq.where(ConsultantTechnology.years_of_experience >= criteria.min_tech_experience)
                
            query = query.where(Consultant.id.in_(subq.subquery()))

        else:
            # ANY Strategy: Consultant matches if they possess at least one requested tech asset
            subq = (
                select(ConsultantTechnology.consultant_id)
                .join(Technology)
                .where(
                    func.lower(Technology.name).in_(cleaned_techs),
                    ConsultantTechnology.deleted_at == None
                )
            )
            
            if criteria.min_tech_experience is not None:
                subq = subq.where(ConsultantTechnology.years_of_experience >= criteria.min_tech_experience)
                
            query = query.where(Consultant.id.in_(subq.subquery()))

    # 3. Inject Core Domain Business State Filters
    if criteria.visa_status:
        query = query.where(Consultant.visa_status.in_(criteria.visa_status))
        
    if criteria.marketing_status:
        query = query.where(Consultant.marketing_status.in_(criteria.marketing_status))
        
    if criteria.current_location:
        query = query.where(Consultant.current_location.ilike(f"%{criteria.current_location}%"))
        
    if criteria.remote_preference:
        query = query.where(Consultant.remote_preference == criteria.remote_preference)

    # 4. Global Text-Box Search (Matches name, email, or current title attributes)
    if criteria.search:
        search_term = f"%{criteria.search}%"
        query = query.where(
            or_(
                Consultant.first_name.ilike(search_term),
                Consultant.last_name.ilike(search_term),
                Consultant.email.ilike(search_term),
                Consultant.current_title.ilike(search_term)
            )
        )

    return query