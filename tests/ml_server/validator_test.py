from ml_server.validator import SentenceValidator


def test_validator(validator: SentenceValidator, sentence_res: tuple[str, bool]):
    assert validator.validate(sentence_res[0]) == sentence_res[1]
