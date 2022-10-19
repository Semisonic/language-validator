from __future__ import annotations
import string


class SentenceValidator:
    _instance: SentenceValidator | None = None

    @classmethod
    def init_instance(cls, path_to_dict: str) -> None:
        cls._instance = SentenceValidator(path_to_dict)

    @classmethod
    def instance(cls) -> SentenceValidator:
        return cls._instance

    def __init__(self, path_to_dict: str) -> None:
        with open(path_to_dict) as dict_file:
            self._bad_words = {l.rstrip() for l in dict_file.readlines()}

    def validate(self, sentence: str) -> bool:
        words = sentence.translate(str.maketrans('', '', string.punctuation)).split()
        return any(w in self._bad_words for w in words)
