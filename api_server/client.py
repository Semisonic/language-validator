import requests
from dataclasses import dataclass


@dataclass
class InPostData:
    title: str
    paragraphs: list[str]


@dataclass
class OutPostData(InPostData):
    hasFoulLanguage: bool | None = None


class Client:
    def __init__(self, host: str, timeout: float) -> None:
        self._host = host
        self._timeout = timeout

    def submit_post(self, post_data: InPostData) -> tuple[int, bool | None]:
        """
        Submit post data to the API server and attempt to receive its language validation.

        The client will register the post at the API server, which will validate its contents
        against a 3rd party foul language detection model.
        Return value is a tuple combining the post's server-side ID and its language validation result.
        If the server load permits, the post contents will be validated immediately and the result provided
        as the second part of the tuple. Otherwise, `None` is returned as the second tuple element, but
        validation will still run in background, so the result could be obtained later via the call to
        `Client.get_post(post_id)`.

        If there's been a connection error, the method will throw an exception inherited from `IOError`.
        """
        res = requests.post(
            self._host + "/posts/",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={"title": post_data.title, "paragraphs": post_data.paragraphs},
            timeout=self._timeout
        )

        res.raise_for_status()
        res_data = res.json()

        return (res_data.get("post_id"), res_data.get("hasFoulLanguage"))

    def get_post(self, post_id: int) -> OutPostData:
        """
        Retrieve data of a previously submitted post.

        This method can be used for deferred language checking of the post's contents.
        If the server has finished checking the post contents, the output
        of this method will have a non-`None` value of `hasFoulLanguage`
        """
        res = requests.get(
            self._host + f"/post/{post_id}",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            timeout=self._timeout
        )

        res.raise_for_status()
        res_data = res.json()

        return OutPostData(res_data.get("title"), res_data.get("paragraphs"), res_data.get("hasFoulLanguage"))
