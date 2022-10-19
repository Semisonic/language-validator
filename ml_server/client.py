import requests


class Client:
    def __init__(self, host: str, timeout: float) -> None:
        self._host = host
        self._timeout = timeout

    def has_foul_language(self, sentence: str) -> bool:
        """
        Validate a sentence against a server-side algorithm.

        This will send a request to a server's endpoint responsible for sentence validation.
        The return value is a boolean flag indicating whether foul language has been detected
        in a supplied sentence.
        If there's been a connection error, the method will throw an exception inherited from `IOError`.
        """
        res = requests.post(
            self._host + "/sentences/",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={"fragment": sentence},
            timeout=self._timeout
        )

        res.raise_for_status()

        return res.json().get("hasFoulLanguage")
