from openai import OpenAI
from app.core.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

# 封装LLM调用
client = OpenAI( # 创建OpenAI客户端
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)

# 定义聊天方法---相当于将你提出的问题发送给大模型
def chat_with_llm(question: str) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "你是 Skybot，一个友好、清晰、可靠的 AI 助手。"},
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content