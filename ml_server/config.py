from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    word_dict_path: str = "ml_server/res/bad_words.txt"  # self-explanatory
    ml_extra_timeout_mean: float = 1.3                   # the higher the number the longer the wait
    ml_max_processing_time: int = 5                      # wait time cutoff
    ml_no_service_probability: int = 5                   # probability (in percents) of producing a 503


@lru_cache()
def settings() -> Settings:
    return Settings()
