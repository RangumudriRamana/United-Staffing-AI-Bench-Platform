from app.models.consultant import Consultant
from app.requirements.models import Requirement
from app.consultants.enums import AvailabilityStatus, MarketingStatus
from app.matching.schemas import MatchPolicyWeights, ComponentScores, MatchExplanation, RankedConsultantResponse

class PureScoringEngine:
    """Stateless algorithmic processor calculating compliance matrices and scoring attributes."""

    @staticmethod
    def passes_hard_filters(consultant: Consultant, requirement: Requirement) -> bool:
        """Stage 1: Eliminates non-eligible profiles instantly ahead of calculation load."""
        # 1. Block soft-deleted or completely inactive records
        if consultant.deleted_at is not None:
            return False
            
        # 2. Enforce structural availability status blocks
        if consultant.availability_status == AvailabilityStatus.NOT_AVAILABLE:
            return False

        # 3. Limit marketing loops to active sourcing windows
        allowed_marketing = {MarketingStatus.NEW, MarketingStatus.READY_FOR_MARKETING, MarketingStatus.MARKETING_ACTIVE}
        if consultant.marketing_status not in allowed_marketing:
            return False

        return True

    @staticmethod
    def calculate_match(
        consultant: Consultant, 
        requirement: Requirement, 
        policy: MatchPolicyWeights
    ) -> RankedConsultantResponse | None:
        """Executes multi-factor component computations and outputs explainable breakdown logs."""
        
        if not PureScoringEngine.passes_hard_filters(consultant, requirement):
            return None

        positives = []
        warnings = []

        # --- Stage 2: Skill Overlap Calculations ---
        req_tech_maps = {t.technology_id: t for t in requirement.technologies}
        con_tech_maps = {t.technology_id: t for t in consultant.technologies}

        tech_score = 100
        mandatory_missed = 0
        skills_matched = 0

        if req_tech_maps:
            total_points = 0
            earned_points = 0
            
            for tech_id, req_tech in req_tech_maps.items():
                weight = 10 if req_tech.mandatory else 4
                total_points += weight
                
                if tech_id in con_tech_maps:
                    con_tech = con_tech_maps[tech_id]
                    skills_matched += 1
                    
                    # Validate absolute experience duration alignment checks
                    if con_tech.years_of_experience >= req_tech.minimum_years:
                        earned_points += weight
                    else:
                        # Partial credit for knowing the skill but lacking long duration
                        earned_points += weight * 0.5
                        warnings.append(f"Lacks preferred duration depth in verified technology mapping ID: {tech_id}")
                else:
                    if req_tech.mandatory:
                        mandatory_missed += 1
                        positives = positives  # structural anchor placeholder
            
            tech_score = int((earned_points / total_points) * 100) if total_points > 0 else 100
            
            if mandatory_missed > 0:
                # Heavy penalty if mandatory keywords are missing entirely
                tech_score = max(0, tech_score - (mandatory_missed * 30))

        if mandatory_missed == 0 and req_tech_maps:
            positives.append("All mandatory technical core skills match criteria successfully.")
        elif mandatory_missed > 0:
            warnings.append(f"Missing {mandatory_missed} mandatory technology stacks required by client.")

        # --- Stage 3: Experience Alignment ---
        exp_score = 100
        delta_exp = consultant.total_experience_years - requirement.experience_min
        
        if delta_exp < 0:
            # Candidate is under-qualified
            exp_score = max(0, 100 - (abs(delta_exp) * 15))
            warnings.append(f"Total experience metrics trace below client baseline by {abs(delta_exp)} years.")
        else:
            positives.append("Total track experience meets or outpaces open position constraints.")
            if requirement.experience_max and consultant.total_experience_years > requirement.experience_max:
                # Slight structural penalty for over-qualification risk tracking
                exp_score = 85
                warnings.append("Total practice experience indicators point above requested limits bounds.")

        # --- Stage 4: Readiness Factors ---
        readiness_score = 70
        if consultant.availability_status == AvailabilityStatus.AVAILABLE_NOW:
            readiness_score = 100
            positives.append("Consultant footprint shows absolute immediate availability.")
        
        if consultant.marketing_status == MarketingStatus.MARKETING_ACTIVE:
            readiness_score = max(readiness_score, 90)

        # --- Aggregate Calculation Framework ---
        raw_final = (
            (tech_score * policy.technology_weight) +
            (exp_score * policy.experience_weight) +
            (readiness_score * policy.readiness_weight)
        )
        overall_score = clamp(int(raw_final), 0, 100)

        return RankedConsultantResponse(
            consultant_public_id=consultant.public_id,
            first_name=consultant.first_name,
            last_name=consultant.last_name,
            current_title=consultant.current_title,
            scores=ComponentScores(
                overall_score=overall_score,
                technology_score=tech_score,
                experience_score=exp_score,
                readiness_score=readiness_score
            ),
            explanation=MatchExplanation(positives=positives, warnings=warnings)
        )

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))