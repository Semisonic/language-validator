from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    word_dict_path: str = "ml_server/res/bad_words.txt"
    ml_extra_timeout_mean: float = 1.3
    ml_max_processing_time: int = 5
    ml_no_service_probability: int = 5


@lru_cache()
def settings() -> Settings:
    return Settings()
