import asyncio
import csv
import time

import httpx
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from config import SHOW_MORE_BUTTON_CLICK_DELAY
from models import Vacancy
from selenium import webdriver
from config import BASE_URL, SKILLS, EXPERIENCE_GROUPS
from selenium.webdriver.support import expected_conditions as EC


async def parse_vacancy(client: httpx.AsyncClient, url: str, exp: str) -> Vacancy:
    response = await client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    soup = soup.select_one(".b-vacancy > .l-vacancy")
    skills = []
    formated_text = soup.get_text().strip().lower()
    for skill in SKILLS:
        if skill.strip().lower() in formated_text:
            skills.append(skill)

    vacancy = Vacancy(
        position=soup.select_one("h1").text,
        experience=exp,
        skills=skills
    )

    places_tag = soup.select_one("span.place")
    if places_tag:
        vacancy.places = places_tag.text.strip().split(",")

    salary_tag = soup.select_one("span.salary")
    if salary_tag:
        salary = salary_tag.text.strip().replace("$", "").split("–")

        if len(salary) != 2:
            return vacancy
        vacancy.salary_min = int(salary[0])
        vacancy.salary_max = int(salary[1])

    return vacancy


async def get_all_vacancies() -> [Vacancy]:
    main_driver = webdriver.Chrome()

    for exp in EXPERIENCE_GROUPS:
        main_driver.get(f"{BASE_URL}&exp={exp}")

        while True:
            try:
                more_button = WebDriverWait(main_driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".more-btn > a"))
                )
                more_button.click()
            except (NoSuchElementException, TimeoutException):
                break
            time.sleep(SHOW_MORE_BUTTON_CLICK_DELAY)

        items = main_driver.find_elements(
            By.CSS_SELECTOR, "#vacancyListId > ul.lt > li.l-vacancy"
        )
        vacancy_urls = []

        for item in items:
            url = item.find_element(By.CSS_SELECTOR, ".title > a.vt").get_attribute("href")
            vacancy_urls.append(url)

        async with httpx.AsyncClient() as client:
            result = await asyncio.gather(
                *[
                    parse_vacancy(client, url, exp)
                    for url in vacancy_urls
                ]
            )

    return result


def write_to_csv(results: [Vacancy]):
    with open('vacancies.csv', 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(['position', 'experience', 'skills', 'salary_min', 'salary_max', 'places'])
        for vacancy in results:
            writer.writerow([
                vacancy.position,
                vacancy.experience,
                vacancy.skills,
                vacancy.salary_min,
                vacancy.salary_max,
                vacancy.places
            ])


async def main():
    vacancies = await get_all_vacancies()
    write_to_csv(vacancies)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    delta = time.time() - start_time
    print(f"Finished in {delta:.2f} seconds")
