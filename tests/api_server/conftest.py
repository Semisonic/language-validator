from pytest import fixture
from api_server.storage import PostDB
from api_server.sentence_queue import SentenceQueue
from api_server.config import Settings


@fixture
def post_db() -> PostDB:
    return PostDB()


@fixture
def sentence_queue() -> SentenceQueue:
    return SentenceQueue()


@fixture(scope="session")
def settings() -> Settings:
    return Settings()
