from abc import ABC
from abc import abstractmethod
import config

from models import Vacancy


class ScrapeVacanciesBase(ABC):
    URL_VARIABLE_NAME: str

    def __init__(self):
        self.BASE_URL = self._get_url()

    @abstractmethod
    def get_all(self) -> list[Vacancy]:
        ...

    def _get_url(self) -> str:
        assert self.URL_VARIABLE_NAME is not None, "Add URL_VARIABLE_NAME property to your scraper class"
        url = getattr(config, self.URL_VARIABLE_NAME, None)
        assert url is not None, f"Add variable {self.URL_VARIABLE_NAME} to config.py"
        return url
