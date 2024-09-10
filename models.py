import csv
from dataclasses import dataclass


@dataclass
class Vacancy:
    position: str
    experience: str = None
    skills: [str] = None
    salary_min: int | None = None
    salary_max: int | None = None
    places: [str] = None

    @staticmethod
    def write_to_csv(vacancies: ["Vacancy"], csv_file: str) -> None:
        if not csv_file.endswith(".csv"):
            csv_file += ".csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["position", "experience", "skills", "salary_min", "salary_max", "places"])
            for vacancy in vacancies:
                writer.writerow([
                    vacancy.position,
                    vacancy.experience,
                    vacancy.skills,
                    vacancy.salary_min,
                    vacancy.salary_max,
                    vacancy.places
                ])
        


