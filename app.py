from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
import dotenv
from fastapi.responses import JSONResponse
from starlette.requests import Request
from utils.cognitive import cogRanker
from utils.rank import analyze_text_async, initializeSentimentAnalysis

dotenv.load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    整个 FastAPI 生命周期的上下文管理器
    :param _: FastAPI 实例
    :return: None
    :param _:
    :return:
    """
    try:
        await initializeSentimentAnalysis()
        # await initializeSpeech2Text()
        yield
    except Exception as e:
        print("Error initializing sentiment analysis models")
        exit(-1)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    """
    Root endpoint
    :return:
    """
    return {"Hello": "World"}


@app.api_route("/api/v1/analyze", methods=["POST", "GET"])
async def analyze(request: Request):
    """
    Analyze the text with azure cognitive services
    :param request: Request
    :return:
    """
    try:
        data = await request.json()
    except Exception as e:
        # todo: return tts: "What the hell are u talking about?"
        print("Error parsing request")
    data = data["text"]
    result = await cogRanker(data)
    if not result:
        # todo: not confident and not cognitive
        print("Error analyzing text")
    else:
        rank = await analyze_text_async(data)
        return JSONResponse(
            content={"success": True, "run": True, "time": str((rank * 10).__round__()), "voiceID": uuid4().hex})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
