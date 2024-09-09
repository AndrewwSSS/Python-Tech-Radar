from dataclasses import dataclass


@dataclass
class Vacancy:
    position: str
    skills: [str]
    experience: str
    salary_min: int | None = None
    salary_max: int | None = None
    places: [str] = None

