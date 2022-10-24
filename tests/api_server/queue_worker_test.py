import pytest
import asyncio
from api_server.queue_worker import sentence_queue_worker, MlClient
from api_server.storage import PostDB, PostData, FoulLanguageStatus
from api_server.sentence_queue import SentenceQueue
from api_server.config import Settings


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sentences,sentence_res",
    [
        (
            ["quick brown fox", "lazy. yellow, bear", " dimwit staff", "mighty! monstrous: mega nugget!!"],
            [False, False, True, True],
        ),
        (
            ["lovely", "beautiful", "language"],
            [False, False, False],
        )
    ]
)
async def test_queue_worker(
    post_db: PostDB, sentence_queue: SentenceQueue, settings: Settings,
    sentences: list[str], sentence_res: list[bool],
    monkeypatch
):
    validation: dict[str, bool] = dict(zip(sentences, sentence_res))

    def dummy_client_call(self, sentence: str) -> bool:
        return validation.get(sentence, False)

    monkeypatch.setattr(MlClient, "has_foul_language", dummy_client_call)

    queue_workers: list[asyncio.Task] = []

    for _ in range(6):
        queue_workers.append(asyncio.create_task(sentence_queue_worker(
            post_db,
            sentence_queue,
            settings,
        )))

    post_id = post_db.insert_new(PostData("just title", sentences))
    completion_event = await sentence_queue.append(post_id, sentences)

    await completion_event.wait()

    assert post_db.posts[post_id].status == FoulLanguageStatus.DETECTED if any(sentence_res) else FoulLanguageStatus.NOT_DETECTED
