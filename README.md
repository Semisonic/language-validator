# language-validator

This is a take home task for [sprout.ai](https://sprout.ai/). The goal is to create a simple server that provides a HTTP REST API designed to accept data resembling a soclal media post, and runs this data past a language validation model which is provided as a separate HTTP service.

The real world language validation model would be a complex ML-based algorithm. For the sake of simplicity, a static dictionary based solution is used for this project.

The main server is also expected to handle occasional unavailability of the language validation service. To make the behaviour of the implemented simple solution more realistic, it waits for a random time for each request, and occasionally generates `Service Unavailable`HTTP errors.


## API call examples
The server is expected to handle requests that look as follows:

    curl -X 'POST' \
      'http://127.0.0.1:5000/posts/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
        "title": "This is an engaging title",
        "paragraphs": [
          "This is the first paragraph. It contains two sentences.",
          "This is the second parapgraph. It contains two more sentences",
          "Third paraphraph here."
        ]
      }'

The language validation service is expected to handle the following requests:

    curl -X 'POST' \
    'http://127.0.0.1:5001/sentences/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "fragment": "This is a sentence that might contain swear words.",
    }'
and respond in a following manner:

     {"hasFoulLanguage": false }

## Functional requirements
The server is expected to provide the following functionality:

 - Accepting posts
 - Storing them in a "database" (which could be an in-memory Python object for the sake of simplicity)
 - Checking if its title or any of its sentences contain foul language
 - Updating the “database” with a flag (let’s call it `hasFoulLanguage`) if there is indeed foul language detected
 
## Tech stack
To run this app, you'll need `python 3.10` and the latest versions of `fastapi`, `uvicorn` and `requests` packages (more outdated versions may also work, but I can't guarantee that).

## Steps to run

To run the API server and the language validation server, download the source code from this repo and set the `PYTHONPATH`environment variable to its root. One way to set it up would be by creating a file named `.env` in the repo root and adding the following line to it:

    PYTHONPATH=.

Then, you need to open a shell of your choosing, `cd` to the repo root folder and launch the language validation service by executing the following command in the shell:

    $ uvicorn ml_server.main:app --host 127.0.0.1 --port 5001 --workers 4

The `--workers 4` argument is optional, but it allows to speed up language validation.

Then, run the main API service by opening _another shell_ and running the following command:

    $ uvicorn api_server.main:app --host 127.0.0.1 --port 5000

Here, it's critical that there's no `--workers` argument, as the "database" used by the API server is a simple in-memory object, which would be duplicated if there was more than one worker.

Now, to use the server you can open _yet another shell_ and run something like `ipython` from it, where you could import the `api_server.client.Client`class and use its well-documented methods to play around with the API server.
Additionally, there's a `ml_server.client.Client` class that wraps around the language validation server's API.

Finally, both the API server and the language validation server provide auto-generated OpenAPI docs (available at http://127.0.0.1:5000/docs and http://127.0.0.1:5001/docs respectively), which allow sending sample requests from the doc pages directly.

## Server configurations
Both API server and language validation server can be configured by modifying their respective `config.py` files. Another way would be to set up environment variables with names matching the names of `api_server.config.Settings` and `ml_server.config.Settings` classes. See [FastAPI docs](https://fastapi.tiangolo.com/advanced/settings/) for more info.

## Issues and limitations
At the moment, there are no automatic tests added, but this will be resolved in the nearest future.
Also, there's a bug which prevents the API server to switch to validating the post contents in background ([post on StackOverflow](https://stackoverflow.com/questions/74132015/asyncio-wait-for-doesnt-time-out-as-expected) that describes it).

## Thanks and greetings
My thanks go to the team of Sprout.ai that gave me the motivation to expand my knowledge of Python web frameworks. Because of this task, I got a chance to pick some knowledge of FastAPI from scratch, and so far I'm definitely impressed with this tool =).

I'd also like to mention my ex-colleague and friend [@akuskis](https://github.com/akuskis) for giving me some extra inspiration to dig deeper and to explore further 🙌.
