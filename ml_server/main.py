import random
from asyncio import sleep
from fastapi import FastAPI, Response, Depends, status
from pydantic import BaseModel, Field, StrictStr, Extra

from ml_server.validator import SentenceValidator
from ml_server.config import settings, Settings


class Sentence(BaseModel, extra=Extra.forbid):
    fragment: StrictStr = Field(title="Sentence to analyse", min_length=1)


class ValidationResult(BaseModel):
    hasFoulLanguage: bool


app = FastAPI()


@app.on_event("startup")
def startup_event():
    SentenceValidator.init_instance(settings().word_dict_path)


@app.post(
    "/sentences/",
    response_model=ValidationResult,
    responses={503: {"model": None}}
)
async def validate(sentence: Sentence, settings: Settings = Depends(settings)):
    # imitating the "service unavailable" scenario
    dice = random.randint(1, 100)

    if dice <= settings.ml_no_service_probability:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    # imitating a slightly varying runtime
    await sleep(min(random.expovariate(1 / settings.ml_extra_timeout_mean), settings.ml_max_processing_time))

    return ValidationResult(hasFoulLanguage=SentenceValidator.instance().validate(sentence.fragment))
