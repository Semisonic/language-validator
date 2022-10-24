import pytest
import asyncio
from api_server.sentence_queue import SentenceQueue


@pytest.mark.asyncio
async def test_sentence_queue(sentence_queue: SentenceQueue):
    sentences = ["one", "two", "three"]
    input_post_id: int = 100

    assert not len(sentence_queue.queue)
    assert not len(sentence_queue._pending_posts)

    async def dummy_worker(queue: SentenceQueue) -> None:
        for cur_sentence_idx in range(len(sentences)):
            async with queue.new_item_cond:
                while not queue.queue:
                    await queue.new_item_cond.wait()

            await asyncio.sleep(0)

            post_id, sentence = queue.queue.popleft()

            assert post_id == input_post_id
            assert sentence == sentences[cur_sentence_idx]

            post_context = queue.on_consume(post_id)

            assert post_context.left_to_process + cur_sentence_idx == len(sentences)

            post_context.left_to_process -= 1

            if not post_context.left_to_process:
                post_context.validation_finished.set()

    worker_task = asyncio.create_task(dummy_worker(sentence_queue))  # noqa: F841
    completion_event = await sentence_queue.append(input_post_id, sentences)

    assert len(sentence_queue.queue) == len(sentences)
    assert len(sentence_queue._pending_posts) == 1
    assert input_post_id in sentence_queue._pending_posts

    await completion_event.wait()

    assert not len(sentence_queue.queue)
    assert not len(sentence_queue._pending_posts)
