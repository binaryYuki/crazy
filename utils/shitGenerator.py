import os
import random
import re

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


async def randomGen(systemOutput: int) -> str:
    """
    生成随机回复
    :param systemOutput:
    :return:
    """
    response_choices = [
        f"But fine, I will warm the food for {systemOutput} seconds."
        f"Alright, I will reheat the meal for {systemOutput} seconds."
        f"Very well, I will microwave the dish for {systemOutput} seconds."
        f"Okay then, I will warm it up for {systemOutput} seconds."
        f"Sure, I will heat the leftovers for {systemOutput} seconds."
        f"Alrighty, I will put the food in the oven for {systemOutput} seconds."
        f"Understood, I will heat the food for {systemOutput} seconds."
        f"No problem, I will warm the food up for {systemOutput} seconds."
        f"Fine then, I will set the timer for heating the food for {systemOutput} seconds."
        f"Sure thing, I will heat the meal for {systemOutput} seconds."
        f"Okay, I will heat the food for {systemOutput} seconds."
    ]
    return response_choices[random.randint(0, len(response_choices) - 1)]


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
            print(response.text)
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
                print(response.text)
                response_txt = response.json()["message"]["content"]
            except Exception as e:
                print(systemOutput)
                runtimes = systemOutput
                response_txt = f"I'm sorry, I cant get you, but i am gonna heat the food for {runtimes} seconds."
                print(f"Error: {e}")
            # 尝试在 txt 中匹配一个整数
            if response_txt:
                try:
                    systemOutput = int(re.search(r'\d+', response_txt).group())
                except Exception as e:
                    phrase = await randomGen(systemOutput)
                    response_txt += phrase
        return response_txt


async def shitWords():
    """
    生成一些脏话
    :return:
    """
    lists = [
        "What on earth are you saying?"
        "What are you going on about?"
        "What in the world do you mean?"
        "What are you rambling on about?"
        "What on earth is that supposed to mean?"
        "Are you serious? What are you talking about?"
        "What are you blathering about?"
        "What the devil are you trying to say?"
        "What on earth are you waffling on about?"
        "What are you on about?"
    ]
    return lists[random.randint(0, len(lists) - 1)]


async def hurtWords():
    ls = [
        "Wow, sounds like a real fun time.",
        "What a unique way to get attention!",
        "Is that the latest trend now? So original.",
        "Ah yes, because that’s definitely the answer.",
        "Brilliant idea, that’s totally not concerning at all.",
        "Oh, please continue. This is riveting.",
        "Because who wouldn’t want to make life harder for themselves?",
        "Fantastic. Just what I wanted to hear.",
        "Clearly, that's one way to handle things.",

    ]
    return ls[random.randint(0, len(ls) - 1)]


async def violentWords():
    ls = ["Ah, nothing like a bit of chaos to spice up life!",
          "Wow, what a charming way to live—who needs peace anyway?",
          "Clearly, we’re doing something right here, aren’t we?",
          "Oh great, just another reason to stay indoors!",
          "Who knew living in a crime scene could be so trendy?",
          "Fabulous! I always wanted a little more excitement in my day-to-day!",
          "Because what’s life without a little violence, right?",
          "Oh joy, that sounds perfectly delightful!",
          "Would you look at that? Just what we needed—more drama!",
          "Nothing like a high violence rate to really get the adrenaline pumping!"]
    return ls[random.randint(0, len(ls) - 1)]


async def hateWords():
    ls = [
        "Oh, what a lovely sentiment! Maybe try kindness next time?",
        "Wow, such positivity! Have you considered compassion instead?",
        "Clearly, spreading hate is the new trend—how original!",
        "Ah, yes, because there’s nothing better than fueling negativity, right?",
        "Perhaps you’d benefit from a little empathy in your life?",
        "Hate has such a charming way of brightening up a conversation!",
        "A little less hate and a bit more understanding could do wonders, you know.",
        "Sounds like you’ve got a real knack for negativity! Ever thought about promoting love instead?",
        "Isn’t it exhausting to be so full of hate? A little kindness might lighten the load.",
        "What a unique perspective! I hear that positivity can actually change the world."
    ]
    return ls[random.randint(0, len(ls) - 1)]



if __name__ == '__main__':
    import asyncio

    asyncio.run(get_openai_response("I love you", {"time": 30}))
