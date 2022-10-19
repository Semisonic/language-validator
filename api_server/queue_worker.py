import logging
from asyncio import sleep
from api_server.storage import PostDB, FoulLanguageStatus
from api_server.sentence_queue import SentenceQueue
from api_server.config import Settings
from ml_server.client import Client as MlClient


async def sentence_queue_worker(db: PostDB, queue: SentenceQueue, settings: Settings) -> None:
    client = MlClient(settings.ml_server_host, settings.ml_request_timeout)

    while True:
        async with queue.new_item_cond:
            while not queue.queue:
                await queue.new_item_cond.wait()

        post_id, sentence = queue.queue.popleft()
        post_context = queue.on_consume(post_id)

        if db.posts[post_id].status == FoulLanguageStatus.DETECTED:
            # foul language already detected, no point checking another sentence

            continue

        check_res: bool | None = None

        while check_res is None:
            try:
                check_res = client.has_foul_language(sentence)
            except IOError as e:
                logging.error("Exceptionn while sending a request to the ML service: %s", e)
                await sleep(settings.ml_request_retry_timeout)

        if check_res:
            db.posts[post_id].status = FoulLanguageStatus.DETECTED
            post_context.validation_finished.set()

            continue

        post_context.left_to_process -= 1

        if not post_context.left_to_process and db.posts[post_id].status == FoulLanguageStatus.PENDING:
            # the last chunk of the post has been processed, no foul language detected
            # we're checking the post status again because another worker could've detected
            # foul language in another chunk since the initial check

            db.posts[post_id].status = FoulLanguageStatus.NOT_DETECTED
            post_context.validation_finished.set()
