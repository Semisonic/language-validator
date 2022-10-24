import pytest
from fastapi.testclient import TestClient
from ml_server.main import app, settings
from ml_server.config import Settings
from ml_server.validator import SentenceValidator


def settings_503() -> Settings:
    settings = Settings()

    settings.ml_no_service_probability = 100

    return settings


def settings_normal() -> Settings:
    settings = Settings()

    settings.ml_no_service_probability = 0
    settings.ml_max_processing_time = 0

    return settings


def test_app_unavailable():
    app.dependency_overrides[settings] = settings_503

    response = TestClient(app).post(
        url="/sentences/",
        json={"fragment": "normal phrase"},
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )

    assert response.status_code == 503


@pytest.mark.parametrize("json", [
    {"fragment": 1},
    {"fragment": ""},
    {"frag": "ment"},
    {"fragment": "valid", "this_one": "not so much"},
])
def test_app_validation(json):
    response = TestClient(app).post(
        url="/sentences/",
        json=json,
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_app(validator: SentenceValidator, sentence_res: tuple[str, bool]):
    app.dependency_overrides[settings] = settings_normal

    old_validator = SentenceValidator._instance
    SentenceValidator._instance = validator

    response = TestClient(app).post(
        url="/sentences/",
        json={"fragment": sentence_res[0]},
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["hasFoulLanguage"] == sentence_res[1]

    SentenceValidator._instance = old_validator
