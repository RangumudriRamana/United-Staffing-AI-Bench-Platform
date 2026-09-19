import pytest

from app.ai_matching.utils import (
    normalize_skills,
    calculate_skill_score,
    calculate_experience_score,
    calculate_visa_score,
    calculate_location_score,
    extract_consultant_technology_names,
    extract_requirement_technology_names,
    calculate_final_match_score,
)


def test_normalize_skills_from_string():
    assert normalize_skills(" Java, Python, java , ") == {"java", "python"}


def test_normalize_skills_from_iterable():
    assert normalize_skills([" Java ", "Python", ""]) == {"java", "python"}


def test_normalize_skills_empty():
    assert normalize_skills(None) == set()
    assert normalize_skills("") == set()


def test_calculate_skill_score():
    score, matched, missing = calculate_skill_score(
        {"java", "python"},
        {"java", "python", "aws"},
    )

    assert score == 66.67
    assert matched == ["java", "python"]
    assert missing == ["aws"]


def test_calculate_skill_score_empty_requirement():
    assert calculate_skill_score({"java"}, set()) == (0.0, [], [])


def test_calculate_experience_score():
    assert calculate_experience_score(5, 3) == 100
    assert calculate_experience_score(2, 4) == 50
    assert calculate_experience_score(None, 4) == 0
    assert calculate_experience_score(4, None) == 0


def test_calculate_visa_score():
    assert calculate_visa_score("H1B", "h1b") == 100
    assert calculate_visa_score("H1B", "F1") == 0
    assert calculate_visa_score(None, "H1B") == 0
    assert calculate_visa_score("H1B", None) == 0


def test_calculate_location_score():
    assert calculate_location_score("Dallas", "dallas") == 100
    assert calculate_location_score("Dallas", "Austin") == 0
    assert calculate_location_score(None, "Dallas") == 0
    assert calculate_location_score("Dallas", None) == 0


def test_extract_technology_names():
    class Technology:
        def __init__(self, name):
            self.name = name

    class ConsultantTechnology:
        def __init__(self, technology):
            self.technology = technology

    class Consultant:
        technologies = [
            ConsultantTechnology(Technology(" Java ")),
            ConsultantTechnology(Technology("Python")),
            ConsultantTechnology(None),
        ]

    assert extract_consultant_technology_names(Consultant()) == {
        "java",
        "python",
    }


def test_extract_requirement_technology_names():
    class Technology:
        def __init__(self, name):
            self.name = name

    class RequirementTechnology:
        def __init__(self, technology):
            self.technology = technology

    class Requirement:
        technologies = [
            RequirementTechnology(Technology(" Java ")),
            RequirementTechnology(Technology("AWS")),
            RequirementTechnology(None),
        ]

    assert extract_requirement_technology_names(Requirement()) == {
        "java",
        "aws",
    }


def test_calculate_final_match_score():
    assert calculate_final_match_score(
        skill_score=100,
        experience_score=100,
        location_score=100,
        visa_score=100,
    ) == 100

    assert calculate_final_match_score(
        skill_score=50,
        experience_score=100,
        location_score=0,
        visa_score=0,
    ) == 50
