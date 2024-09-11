import asyncio
import time

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Scrapers.BaseScraper import ScrapeVacanciesBase
from config import DOU_EXPERIENCE_GROUPS
from config import DOWNLOAD_GROUPS_COUNT
from config import DOWNLOAD_GROUPS_DELAY
from config import SHOW_MORE_BUTTON_CLICK_DELAY
from config import SKILLS
from models import Vacancy


class DouScraper(ScrapeVacanciesBase):
    URL_VARIABLE_NAME = "DOU_URL"

    @staticmethod
    def split_list(lst, n):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    @staticmethod
    async def _parse_vacancy(
        client: httpx.AsyncClient, url: str, exp: str
    ) -> Vacancy:
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

    async def get_all(self) -> [Vacancy]:
        main_driver = webdriver.Chrome()
        vacancy_urls = []

        for exp in DOU_EXPERIENCE_GROUPS:
            main_driver.get(f"{self.BASE_URL}&exp={exp}")

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

            for item in items:
                url = item.find_element(By.CSS_SELECTOR, ".title > a.vt").get_attribute("href")
                vacancy_urls.append((url, exp))

        result = []

        async with httpx.AsyncClient() as client:
            for index, group in enumerate(self.split_list(vacancy_urls, DOWNLOAD_GROUPS_COUNT)):
                group_result = await asyncio.gather(
                    *[
                        self._parse_vacancy(client, url, exp)
                        for url, exp in group
                    ]
                )
                result.extend(group_result)
                print(f"{index+1} group done")
                time.sleep(DOWNLOAD_GROUPS_DELAY)

        return result
