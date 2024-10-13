import os
import httpx
import dotenv


class notSexualEnoughError(Exception):
    """
    Not sexual enough
    """
    pass


async def cogRanker(text: str) -> tuple:
    """
    Analyze the text with azure cognitive services
    :param text:
    """
    endpoint = "https://binaryyuki.cognitiveservices.azure.com/"
    path = "/contentsafety/text:analyze?api-version=2023-10-01"
    url = endpoint + path
    headers = {
        "Ocp-Apim-Subscription-Key": os.environ.get("AZURE_API_KEY"),
        "Content-Type": "application/json"
    }
    body = {
        "text": text
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)

    data = response.json()
    try:
        hateRate = data["categoriesAnalysis"][0]["severity"]
        selfHarmRate = data["categoriesAnalysis"][1]["severity"]
        sexualRate = data["categoriesAnalysis"][2]["severity"]
        violenceRate = data["categoriesAnalysis"][3]["severity"]
        print(f"Hate Rate: {hateRate}")
        print(f"Self Harm Rate: {selfHarmRate}")
        print(f"Sexual Rate: {sexualRate}")
        print(f"Violence Rate: {violenceRate}")
    except Exception as e:
        print(f"Error: {e}")

    # 综合评分 计算是否允许进行下一步操作
    if sexualRate >= 1:
        return True, sexualRate, hateRate, selfHarmRate, violenceRate
    if hateRate > 0.5 or selfHarmRate > 0.5 or sexualRate > 0.5 or violenceRate > 0.5:
        return False, sexualRate, hateRate, selfHarmRate, violenceRate
    else:
        return True, sexualRate, hateRate, selfHarmRate, violenceRate


if __name__ == '__main__':
    import asyncio

    asyncio.run(cogRanker("I love you"))
