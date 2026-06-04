from app.core.llm import chat_with_llm

# 写Skybot主逻辑
# 先创建一个最简单的 Agent 对象。现在它只会调用 LLM，后面工具、记忆都会加到这里。
class Skybot:
    def chat(self, question: str) -> str:
        return chat_with_llm(question)
