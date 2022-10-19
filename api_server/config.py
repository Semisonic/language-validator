from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    ml_server_host: str = "http://127.0.0.1:5001"  # self-explanatory
    ml_request_timeout: float = 10.0               # time before requests to ML service timeout
    ml_request_processor_count: int = 6            # number of async workers to send requests to ML service
    ml_request_retry_timeout: float = 1.0          # waiting time before retries in case a request to ML service failed
    sentence_queue_sync_response_threshold = 50    # if the amount of sentences in the queue is higher, validation will run in background
    sentence_queue_rejection_threshold = 5000      # if the amount of sentences in the queue is higher, new posts will be rejected
    sync_wait_timeout: float = 3.0                 # if validation takes more than this time, the request will return prematurely (BUGGY at the moment)


@lru_cache()
def settings() -> Settings:
    return Settings()
