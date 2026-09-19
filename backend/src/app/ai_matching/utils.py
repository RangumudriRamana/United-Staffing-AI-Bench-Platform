from typing import Iterable


def normalize_skills(skills: str | Iterable[str] | None) -> set[str]:
    if not skills:
        return set()

    if isinstance(skills, str):
        items = skills.split(",")
    else:
        items = skills

    return {
        skill.strip().lower()
        for skill in items
        if skill and skill.strip()
    }


def calculate_skill_score(
    consultant_skills: set[str],
    requirement_skills: set[str],
) -> tuple[float, list[str], list[str]]:

    matched = sorted(
        consultant_skills.intersection(requirement_skills)
    )

    missing = sorted(
        requirement_skills.difference(consultant_skills)
    )

    if not requirement_skills:
        return 0.0, matched, missing

    score = (
        len(matched) / len(requirement_skills)
    ) * 100

    return round(score, 2), matched, missing

def calculate_experience_score(
    consultant_exp: float | None,
    required_exp: float | None,
) -> float:

    if consultant_exp is None or required_exp is None:
        return 0

    if consultant_exp >= required_exp:
        return 100

    return round((consultant_exp / required_exp) * 100, 2)


def calculate_visa_score(
    consultant_visa: str | None,
    required_visa: str | None,
) -> float:

    if not consultant_visa or not required_visa:
        return 0

    return (
        100
        if consultant_visa.lower() == required_visa.lower()
        else 0
    )


def calculate_location_score(
    consultant_location: str | None,
    required_location: str | None,
) -> float:

    if not consultant_location or not required_location:
        return 0

    return (
        100
        if consultant_location.lower() == required_location.lower()
        else 0
    )

def extract_consultant_technology_names(consultant) -> set[str]:
    return {
        technology.technology.name.strip().lower()
        for technology in consultant.technologies
        if technology.technology
    }


def extract_requirement_technology_names(requirement) -> set[str]:
    return {
        technology.technology.name.strip().lower()
        for technology in requirement.technologies
        if technology.technology
    }

def calculate_final_match_score(
    skill_score: float,
    experience_score: float,
    location_score: float,
    visa_score: float,
) -> float:
    """
    Enterprise weighted scoring.

    Skills      : 60%
    Experience  : 20%
    Location    : 10%
    Visa         : 10%
    """

    return round(
        (
            skill_score * 0.60
            + experience_score * 0.20
            + location_score * 0.10
            + visa_score * 0.10
        ),
        2,
    )