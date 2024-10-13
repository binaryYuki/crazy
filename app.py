import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
import dotenv
from fastapi.responses import JSONResponse
from starlette.requests import Request
from utils.cognitive import cogRanker
from utils.rank import analyze_text_async, initializeSentimentAnalysis
from utils.shitGenerator import get_openai_response, shitWords

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


"""
response model:
{
    "success": True,
    "run": True,
    "time": 30,
    "response": "I love you"
}
"""


@app.api_route("/api/v1/response", methods=["POST", "GET"])
async def response(request: Request):
    """
    Response endpoint
    :param request:
    :return:
    """
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse(
            content={"success": False, "response": "What the hell are u talking about?", "time": "0", "run": False})
    try:
        data = data["text"]
        print(f"Data: {data}")
    except Exception as e:
        return JSONResponse(
            content={"success": False, "response": shitWords(), "time": "0", "run": False})

    result, bonus = await cogRanker(data)
    if not result:
        return JSONResponse(
            content={"success": True, "run": False, "time": str(0), "response": shitWords()})
    else:
        rank = await analyze_text_async(data)
        print(f"Rank: {rank}", f"Bonus: {bonus}")
        rank += (bonus / 10) * 3
        responseText = await get_openai_response(data, str((rank * 10).__round__()))
        if rank != 0:
            rank = (rank * 10).__round__() + 3
        else:
            rank = 0
        return JSONResponse(
            content={
                "success": True,
                "run": True,
                "time": str(rank),
                "response": responseText
            })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
