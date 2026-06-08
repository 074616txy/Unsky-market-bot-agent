from app.core.llm import chat_with_llm
from app.tools.product_tool import search_product
import json
from app.memory.simple_memory import SimpleMemory


# 写Skybot主逻辑
# 日志：
# 1.先创建一个最简单的 Agent 对象。现在它只会调用 LLM，后面工具、记忆都会加到这里。
# 2.补充上最小工具调用的闭环----调用search_product_mock实现模拟二手商品数据的搜索。
# 3.新增由LLM决策式调用工具的方法，关于工具的调用直接让LLM选择并实施，在chat方法里使用新工具。
# 4.给skybot新增短期对话记录记忆memory，实现基本的短期记忆，为后续加入大型记忆知识库做铺垫。
# 5.在product_tool里面实现统一调用入口，并将代码逻辑从模拟商品搜索转为真实接口调用
class Skybot:
#    day03修改对应的chat方法--新增_decide_tool()LLM决策式工具调用
#    def chat(self, question: str) -> str:
#       # 前置条件：查看需不需要调用工具，工具有结果，直接将结果返还给llm，让llm组织自然语言回答
#        tool_result = self._try_use_tool(question) # 带着问题去尝试调用工具
#
#        if tool_result: # 判断工具是否有结果
#            prompt = self._build_tool_prompt(question, tool_result)
#            return chat_with_llm(prompt) # 由于工具只能给出数据，所以需要llm解释数据
#
#        return chat_with_llm(question)
#    # 修改chat方法
#    def chat(self, question: str) -> str:
#        decision = self._decide_tool(question)
#
#        if decision.get("use_tool"):
#            tool_name = decision.get("tool_name")
#            arguments = decision.get("arguments", {})
#
#            if tool_name == "search_product":
#                keyword = arguments.get("keyword", question)
#                tool_result = search_product_mock(keyword)
#
#                prompt = self._build_tool_prompt(question, tool_result)
#                return chat_with_llm(prompt)
#
#        return chat_with_llm(question)

    def chat(self, question: str) -> str:
        memory_context = self.memory.get_context() # 对话前获取上下文

        question_with_memory = self._build_memory_prompt(question, memory_context)

        decision = self._decide_tool(question_with_memory)

        if decision.get("use_tool"):
            tool_name = decision.get("tool_name")
            arguments = decision.get("arguments", {})

            if tool_name == "search_product":
                keyword = arguments.get("keyword", question)
                tool_result = search_product(keyword,use_api=False)

                prompt = self._build_tool_prompt(question_with_memory, tool_result)
                answer = chat_with_llm(prompt)
                # 对话后保存用户和agent的对话记录，方便下一轮对话作为上下文被读取
                self.memory.add_user_message(question)
                self.memory.add_assistant_message(answer)

                return answer

        answer = chat_with_llm(question_with_memory)

        self.memory.add_user_message(question)
        self.memory.add_assistant_message(answer)

        return answer

    # _try_use_tool() 负责获取外部真实数据
    def _try_use_tool(self, question: str) -> str | None:
        product_keywords = ["商品", "手机", "电脑", "推荐", "价格", "二手"]

        if any(keyword in question for keyword in product_keywords):
            keyword = self._extract_product_keyword(question)
            return search_product(keyword)

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

    # _decide_tool()负责让Agent寻求LLM关于工具的调用的想法与具体实施方案
    def _decide_tool(self, question: str) -> dict:
        tool_prompt = f"""
    你是 Skybot 的工具决策模块。

    你需要判断用户问题是否需要调用工具。

    当前可用工具：
    1. search_product
       作用：搜索二手商品模拟数据
       参数：
       - keyword: 商品关键词，例如 手机、电脑、iPhone、华为

    用户问题：
    {question}

    请严格返回 JSON，不要输出任何解释文字。

    如果需要调用工具，返回：
    {{
      "use_tool": true,
      "tool_name": "search_product",
      "arguments": {{
        "keyword": "关键词"
      }}
    }}

    如果不需要调用工具，返回：
    {{
      "use_tool": false,
      "tool_name": null,
      "arguments": {{}}
    }}
    """

        result = chat_with_llm(tool_prompt)

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "use_tool": False,
                "tool_name": None,
                "arguments": {},
            }
    # 短期记忆初始化
    def __init__(self):
        self.memory = SimpleMemory(max_rounds=5) # 保留最大5轮对话

    # 建造记忆提示词来将对话历史和用户提问作为历史上下文
    def _build_memory_prompt(self, question: str, memory_context: str) -> str:
        if not memory_context:
            return question

        return f"""
        以下是最近的对话历史：
        {memory_context}
    
        用户当前问题：
        {question}
    
        请结合对话历史回答当前问题。
        """