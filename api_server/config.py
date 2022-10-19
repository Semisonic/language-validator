from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    ml_server_host: str = "http://127.0.0.1:5001"
    ml_request_timeout: float = 10.0
    ml_request_processor_count: int = 6
    ml_request_retry_timeout: float = 1.0
    sentence_queue_sync_response_threshold = 50
    sentence_queue_rejection_threshold = 5000
    sync_wait_timeout: float = 3.0


@lru_cache()
def settings() -> Settings:
    return Settings()
