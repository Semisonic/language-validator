from __future__ import annotations
from asyncio import Event, Condition
from collections import deque
from dataclasses import dataclass


@dataclass
class PostContext:
    left_to_consume: int
    left_to_process: int
    validation_finished: Event


class SentenceQueue:
    _instance: SentenceQueue | None = None

    @classmethod
    def init_instance(cls) -> None:
        cls._instance = SentenceQueue()

    @classmethod
    def instance(cls) -> SentenceQueue:
        return cls._instance

    def __init__(self) -> None:
        self.new_item_cond = Condition()
        self._pending_posts: dict[int, PostContext] = {}
        self.queue: deque[tuple[int, str]] = deque()

    async def append(self, post_id: int, sentences: list[str]) -> Event:
        assert post_id not in self._pending_posts

        post_event = Event()
        self._pending_posts[post_id] = PostContext(len(sentences), len(sentences), post_event)

        for s in sentences:
            self.queue.append((post_id, s))

        async with self.new_item_cond:
            self.new_item_cond.notify_all()

        return post_event

    def on_consume(self, post_id: int) -> PostContext:
        """
        Informs the queue of a sentence consumption.

        A queue worker must do that after having popped an item from the queue's head.
        This will lead to the queue marking that sentence as processed. It's the worker's
        responsibility to mark the post event as set if the processing result is known.
        """

        mc = self._pending_posts[post_id]

        mc.left_to_consume -= 1

        if not mc.left_to_consume:
            self._pending_posts.pop(post_id)

        return mc
