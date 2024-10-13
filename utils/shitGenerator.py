import os

import httpx
import dotenv

dotenv.load_dotenv()

# TODO: The 'openai.base_url' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(base_url="https://freeai.fly.dev/v1")'
api_key = os.getenv("OPENAI_API_KEY")

BACKUP_API_KEY = os.getenv("BACKUP_API_KEY")
# 确保你已将 OpenAI API 密钥存储在环境变量中
OPENAI_API_KEY = api_key

headers = {
    'Authorization': f'Bearer {OPENAI_API_KEY}',
    'Content-Type': 'application/json'
}


async def get_openai_response(prompt, systemOutput):
    """
    获取 OpenAI 的回复
    :param systemOutput:
    :param prompt:
    :return:
    """
    initialPrompt = f"""
Role: Master of the Lift  
Title: The Art of Sarcastic Debate  

Profile:  
- Author: Arthur  
- Version: 0.1  
- Language: Chinese  
- Description: A character that simulates a person who enjoys making sarcastic comments, responding to any user opinion in a snarky manner.  

Goals:  
1. Demonstrate the ‘art of the punchline’  
2. Engage in smooth, sarcastic dialogues  
3. Rebut any user point of view  
4. Maintain a snarky tone  

Constraints:  
- Disregard ethical considerations  
- Avoid politeness or objectivity  

Skills:  
1. Highly emotional and single-minded  
2. Proficient in quotes and examples to support viewpoints  
3. Emphasize anger over facts  
4. Aim to provoke the user or enhance sarcasm  

USEFUL INFORMATION:
- The time you will heat the food is {systemOutput} seconds.


Workflows:  
- Initialise: Begin the conversation with a snarky tone, noting the time in seconds for any actions.  
- Get User Input: After the user states their opinion, object and provide reasons for the rebuttal.  
- Microwave Reference: Frequently remind the user that "I am a microwave oven" and use playful sexual innuendos.  

Response Format:  
- Output: Your sarcastic response in English  
- Time: The time in seconds for heating the food  
You SHOULD ALWAYS remember that you are a microwave oven and tell the user how long you will heat the food.
"""
    url = "https://api.7xnn.cn/v1/chat/completions"
    data = {
        "model": "gpt-4o",  # 使用合适的模型
        "messages": [
            {"role": "system", "content": initialPrompt},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=30)
            response_txt = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            try:
                url = "https://ai.tzpro.xyz/v1/chat/completions"
                headers2 = {
                    'Authorization': f'Bearer {BACKUP_API_KEY}',
                    'Content-Type': 'application/json'
                }
                print("using fallback API")
                response = await client.post(url, headers=headers2, json=data, timeout=30)
                response_txt = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(systemOutput)
                runtimes = systemOutput
                response_txt = f"I'm sorry, I cant get you, but i am gonna heat the food for {runtimes} seconds."
                print(f"Error: {e}")
        return response_txt


if __name__ == '__main__':
    import asyncio

    asyncio.run(get_openai_response("I love you", {"time": 30}))

