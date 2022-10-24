from pytest import fixture
from ml_server.validator import SentenceValidator


@fixture(scope="session")
def validator() -> SentenceValidator:
    return SentenceValidator("tests/ml_server/res/bad_words.txt")


@fixture(
    params=[
        ("quick brown fox", False),
        ("lazy. yellow, bear", False),
        (" dimwit staff", True),
        ("mighty! monstrous: mega nugget!!", True)
    ]
)
def sentence_res(request) -> tuple[str, bool]:
    return request.param
