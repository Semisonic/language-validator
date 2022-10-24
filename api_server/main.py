import logging
from asyncio import Task, create_task, TimeoutError, wait_for
from fastapi import FastAPI, Response, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from api_server.config import settings, Settings
from api_server.queue_worker import sentence_queue_worker
from api_server.sentence_queue import SentenceQueue
from api_server.storage import PostDB, PostData, FoulLanguageStatus


class Post(BaseModel):
    title: str = Field(min_length=1)
    paragraphs: list[str] = Field(min_items=1)


class SubmissionResult(BaseModel):
    post_id: int
    hasFoulLanguage: bool | None
    language_check_pending: bool | None


class PostOut(Post):
    hasFoulLanguage: bool | None


class ServiceUnavailable(BaseModel):
    message: str = "Too many unprocessed posts. A new post cannot be registered."


app = FastAPI()
queue_workers: list[Task] = []
logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)


@app.on_event("startup")
async def startup_event():
    PostDB.init_instance()
    SentenceQueue.init_instance()

    for _ in range(settings().ml_request_processor_count):
        queue_workers.append(create_task(sentence_queue_worker(
            PostDB.instance(),
            SentenceQueue.instance(),
            settings(),
        )))


@app.post(
    "/posts/",
    response_model=SubmissionResult,
    response_model_exclude_unset=True,
    responses={503: {"model": ServiceUnavailable}}
)
async def store_and_validate(post: Post, settings: Settings = Depends(settings)):
    sentences: list[str] = [post.title]

    for p in post.paragraphs:
        sentences.extend(f for f in p.split(".") if f)

    queue = SentenceQueue.instance()
    db = PostDB.instance()

    if (sentence_count := len(queue.queue) + len(sentences)) > settings.sentence_queue_rejection_threshold:
        return JSONResponse(content=ServiceUnavailable().json(), status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    post_id = db.insert_new(PostData(post.title, post.paragraphs))
    completion_event = await queue.append(post_id, sentences)

    if sentence_count > settings.sentence_queue_sync_response_threshold:
        return SubmissionResult(post_id=post_id, language_check_pending=True)

    try:
        await wait_for(completion_event.wait(), settings.sync_wait_timeout)
    except TimeoutError:
        logging.info("Post failed to process synchronously within given time, returning pending status...")
        return SubmissionResult(post_id=post_id, language_check_pending=True)

    return SubmissionResult(
        post_id=post_id,
        hasFoulLanguage=(db.posts[post_id].status == FoulLanguageStatus.DETECTED)
    )


@app.get(
    "/post/{post_id}",
    response_model=PostOut,
    response_model_exclude_unset=True,
    responses={404: {"model": None}}
)
def get_post_data(post_id: int):
    db = PostDB.instance()

    if post_id >= len(db.posts):
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    post_data = db.posts[post_id]
    res = PostOut(title=post_data.title, paragraphs=post_data.paragraphs)

    if post_data.status != FoulLanguageStatus.PENDING:
        res.hasFoulLanguage = (post_data.status == FoulLanguageStatus.DETECTED)

    return res
