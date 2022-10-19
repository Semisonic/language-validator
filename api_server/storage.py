from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class FoulLanguageStatus(Enum):
    DETECTED = auto()
    NOT_DETECTED = auto()
    PENDING = auto()


@dataclass
class PostData:
    title: str
    paragraphs: list[str]
    status: FoulLanguageStatus = FoulLanguageStatus.PENDING


class PostDB:
    _instance: PostDB | None = None

    @classmethod
    def init_instance(cls) -> None:
        cls._instance = PostDB()

    @classmethod
    def instance(cls) -> PostDB:
        return cls._instance

    def __init__(self) -> None:
        self.posts: list[PostData] = []

    def insert_new(self, data: PostData) -> int:
        self.posts.append(data)

        return len(self.posts) - 1
