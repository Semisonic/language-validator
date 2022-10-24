import pytest
from fastapi.testclient import TestClient
from api_server.main import app, settings
from api_server.config import Settings
from api_server.queue_worker import MlClient


def settings_normal() -> Settings:
    return Settings()


def settings_async() -> Settings:
    settings = settings_normal()
    settings.sentence_queue_sync_response_threshold = 0

    return settings


def settings_unavailable() -> Settings:
    settings = settings_async()
    settings.sentence_queue_rejection_threshold = 0

    return settings


def test_app_unavailable():
    app.dependency_overrides[settings] = settings_unavailable

    with TestClient(app) as client:
        response = client.post(
            url="/posts/",
            json={"title": "normal phrase", "paragraphs": ["one", "two", "three"]},
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )

    assert response.status_code == 503


@pytest.mark.parametrize("json", [
    {"title": 1},
    {"title": ""},
    {"title": "just title, no content"},
    {"paragraphs": ""},
    {"paragraphs": [""]},
    {"paragraphs": ["just content, no title"]},
    {"title": "title ok", "paragraphs": "bad format"},
    {"title": "title ok", "paragraphs": []},
    {"title": "title ok", "paragraphs": ["sometimes maybe good", "", "sometimes maybe empty"]},
    {"title": 1, "paragraphs": ["content ok"]},
    {"title": "", "paragraphs": ["content ok"]},
    {"title": "title ok", "paragraphs": ["content ok"], "extra": "unexpected"},
])
def test_app_validation(json):
    response = TestClient(app).post(
        url="/posts/",
        json=json,
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_app_async(monkeypatch):
    app.dependency_overrides[settings] = settings_async

    def noop_client_call(self, sentence: str) -> bool:
        return False

    monkeypatch.setattr(MlClient, "has_foul_language", noop_client_call)

    with TestClient(app) as client:
        title = "normal phrase"
        paragraphs = ["one. two. three, four", "five: six. seven - eight"]

        response = client.post(
            url="/posts/",
            json={"title": title, "paragraphs": paragraphs},
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert response.json()["post_id"] == 0

        response = client.get(
            url="/post/0",
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == title
        assert data["paragraphs"] == paragraphs
        assert not data["hasFoulLanguage"]

        response = client.get(
            url="/post/1",
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )

        assert response.status_code == 404


@pytest.mark.parametrize(
    "paragraphs,paragraph_res",
    [
        (
            ["quick brown fox", "lazy. yellow, bear", " dimwit staff.", "mighty! monstrous: mega nugget!!"],
            [False, False, True, True],
        ),
        (
            ["beautiful title", "a paragraph. with multiple sentences.", "another one. even more eloquent!"],
            [False, False, False],
        )
    ]
)
def test_app(paragraphs: list[str], paragraph_res: list[bool], monkeypatch):
    app.dependency_overrides[settings] = settings_normal

    validation: dict[str, bool] = {}

    for paragraph, res in zip(paragraphs, paragraph_res):
        sentences = [s for s in paragraph.split(".") if s]

        for s in sentences:
            validation[s] = res

    def dummy_client_call(self, sentence: str) -> bool:
        return validation.get(sentence)

    monkeypatch.setattr(MlClient, "has_foul_language", dummy_client_call)

    with TestClient(app) as client:
        response = client.post(
            url="/posts/",
            json={"title": paragraphs[0], "paragraphs": paragraphs[1:]},
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert response.json()["hasFoulLanguage"] == any(paragraph_res)
