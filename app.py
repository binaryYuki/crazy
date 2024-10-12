from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
import dotenv
from fastapi.responses import JSONResponse
from starlette.requests import Request
from utils.cognitive import cogRanker
from utils.rank import analyze_text_async, initializeSentimentAnalysis
from utils.shitGenerator import get_openai_response

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
    try:
        data = data["text"]
        print(f"Data: {data}")
    except Exception as e:
        return JSONResponse(
            content={"success": False, "run": False, "time": str(0), "voiceID": uuid4().hex})
    result, bonus = await cogRanker(data)
    print(f"Result: {result}, Bonus: {bonus}")
    if not result:
        # todo: not confident and not cognitive
        return JSONResponse(
            content={"success": True, "run": False, "time": str(0), "voiceID": uuid4().hex})
    else:
        rank = await analyze_text_async(data)
        print(f"Rank: {rank}", f"Bonus: {bonus}")
        rank += (bonus / 10) * 3
        if rank < 0.5:  # minimum rank is 0.5 means it's not sexual enough
            return JSONResponse(
                content={"success": True, "run": False, "time": str(0), "voiceID": uuid4().hex})
        return JSONResponse(
            content={"success": True, "run": True, "time": str((rank * 10).__round__() + 20), "voiceID": uuid4().hex})


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
            content={"success": False, "response": "What the hell are u talking about?"})
    try:
        data = data["text"]
        print(f"Data: {data}")
    except Exception as e:
        return JSONResponse(
            content={"success": False, "response": "What the hell are u talking about?"})
    response = await get_openai_response(data)
    return JSONResponse(content={"success": True, "response": response})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    # command: uvicorn app:app --reload --host 0.0.0.0 --port 8000 --workers 4
