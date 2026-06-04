from app.core.llm import chat_with_llm
from app.tools.product_tool import search_product_mock

# 写Skybot主逻辑
# 日志：
# 1.先创建一个最简单的 Agent 对象。现在它只会调用 LLM，后面工具、记忆都会加到这里。
# 2.补充上最小工具调用的闭环----调用search_product_mock实现模拟二手商品数据的搜索。
class Skybot:
    def chat(self, question: str) -> str:
        # 前置条件：查看需不需要调用工具，工具有结果，直接将结果返还给llm，让llm组织自然语言回答
        tool_result = self._try_use_tool(question) # 带着问题去尝试调用工具

        if tool_result: # 判断工具是否有结果
            prompt = self._build_tool_prompt(question, tool_result)
            return chat_with_llm(prompt) # 由于工具只能给出数据，所以需要llm解释数据

        return chat_with_llm(question)

    # _try_use_tool() 负责获取外部真实数据
    def _try_use_tool(self, question: str) -> str | None:
        product_keywords = ["商品", "手机", "电脑", "推荐", "价格", "二手"]

        if any(keyword in question for keyword in product_keywords):
            keyword = self._extract_product_keyword(question)
            return search_product_mock(keyword)

        return None

    # _extract_product_keyword()简单提取问题中的关键字
    def _extract_product_keyword(self, question: str) -> str:
        if "手机" in question:
            return "手机"
        if "电脑" in question:
            return "电脑"
        if "苹果" in question or "iPhone" in question:
            return "iPhone"
        if "华为" in question:
            return "华为"

        return question

    # _build_tool_prompt() 负责将工具结果注入上下文
    def _build_tool_prompt(self, question: str, tool_result: str) -> str:
        return f"""
用户问题：
{question}

以下是工具查询到的商品信息：
{tool_result}

请你基于这些商品信息回答用户问题。
如果商品信息不足，请明确说明，不要编造不存在的商品。
"""