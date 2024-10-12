import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# 初始化情感分析器
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
# 初始化情感分析模型
sentiment_pipeline = pipeline('sentiment-analysis')


async def initializeSentimentAnalysis():
    """
    Initialize the sentiment analysis models
    """
    # 初始化情感分析器
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    # 初始化情感分析模型
    sentiment_pipeline = pipeline('sentiment-analysis')
    return sia, sentiment_pipeline




def analyze_text(text: str) -> float:
    """
    Analyze the polarity of the word
    :param text:
    :return:
    """
    # 使用情感分析器进行评分
    scores = sia.polarity_scores(text)

    # 提取正面评分
    positive_score = scores['pos']
    return positive_score


def analyze_text_llm(text):
    """
    Analyze the polarity of the word with transformer model
    :param text:
    :return:
    """
    # 分析文本
    results = sentiment_pipeline(text)
    for result in results:
        if result['label'] == 'POSITIVE':
            return result['score']
        elif result['label'] == 'NEGATIVE':
            return 1 - result['score']
    return 0.5


async def analyze_text_async(text: str) -> float:
    """
    use both transformer models and nltk to analyze the polarity of the word and return the average score
    :param text:
    :return:
    """
    # 使用transformer模型进行评分
    transformer_score = analyze_text_llm(text)

    # 使用情感分析器进行评分
    nltk_score = analyze_text(text)

    # 返回两个评分的平均值
    return (transformer_score + nltk_score) / 2


if __name__ == '__main__':
    text = "What the hell is this?"
    import asyncio
    asyncio.run(initializeSentimentAnalysis())
    result = asyncio.run(analyze_text_async(text))
    print(result)
