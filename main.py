import asyncio
import time

from dotenv import load_dotenv

from Scrapers.DouScraper import DouScraper
from models import Vacancy


async def main():
    vacancies = await DouScraper().get_all()
    Vacancy.write_to_csv(vacancies, "result.csv")

if __name__ == "__main__":
    load_dotenv()
    start_time = time.time()
    asyncio.run(main())
    delta = time.time() - start_time
    print(f"Finished in {delta:.2f} seconds")
