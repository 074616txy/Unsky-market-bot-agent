from app.core.llm import chat_with_llm
from app.tools.product_tool import search_product, get_product_detail_from_api
import json
from app.memory.simple_memory import SimpleMemory
from app.tools.product_tool import get_product_detail_from_api, search_product_list_from_api


# 写Skybot主逻辑
# 日志：
# 1.先创建一个最简单的 Agent 对象。现在它只会调用 LLM，后面工具、记忆都会加到这里。
# 2.补充上最小工具调用的闭环----调用search_product_mock实现模拟二手商品数据的搜索。
# 3.新增由LLM决策式调用工具的方法，关于工具的调用直接让LLM选择并实施，在chat方法里使用新工具。
# 4.给skybot新增短期对话记录记忆memory，实现基本的短期记忆，为后续加入大型记忆知识库做铺垫。
# 5.在product_tool里面实现统一调用入口，并将代码逻辑从模拟商品搜索转为真实接口调用
# 6.提高商品的分析能力，补充并新增提示词Prompt来增强LLM对具体商品数据的分析
# 7.实现相应商品搜索能力，可以搜索具体用户所需要的商品类型，进一步满足用户的真实需求
# 8.拓展skybot关于用户个性化信息的功能，让用户可以在skybot里面实现查询相关用户信息以及对应的商品信息
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
#    # day04修改chat方法
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
#    # day06修改chat方法
#    def chat(self, question: str) -> str:
#        memory_context = self.memory.get_context() # 对话前获取上下文
#
#        question_with_memory = self._build_memory_prompt(question, memory_context)
#
#        decision = self._decide_tool(question_with_memory)
#
#        if decision.get("use_tool"):
#            tool_name = decision.get("tool_name")
#            arguments = decision.get("arguments", {})
#
#            if tool_name == "search_product":
#                keyword = arguments.get("keyword", question)
#                tool_result = search_product(keyword,use_api=False)
#
#                prompt = self._build_tool_prompt(question_with_memory, tool_result)
#                answer = chat_with_llm(prompt)
#                # 对话后保存用户和agent的对话记录，方便下一轮对话作为上下文被读取
#                self.memory.add_user_message(question)
#                self.memory.add_assistant_message(answer)
#
#                return answer
#
#       answer = chat_with_llm(question_with_memory)
#
#        self.memory.add_user_message(question)
#        self.memory.add_assistant_message(answer)
#
#        return answer
    # 补充完善chat()方法
    def chat(
            self,
            question: str,
            user_id: int | None = None,
            scene: str | None = None,
            product_id: int | None = None,
            user_context: dict = None
    ) -> dict:
        memory_context = self.memory.get_context()
        question_with_memory = self._build_memory_prompt(question, memory_context)

        # 如果请求中直接带有product_id，那么直接调用函数查具体商品的详情数据
        if product_id is not None:
            product_detail = get_product_detail_from_api(product_id)

            if scene == "product_analysis":
                prompt = self._build_product_analysis_prompt(question, product_detail)
            else:
                prompt = self._build_product_detail_prompt(question, product_detail)

            answer = chat_with_llm(prompt)

            self.memory.add_user_message(question)
            self.memory.add_assistant_message(answer)

            return {
                "answer": answer,
                "used_tool": True,
                "tool_name": "get_product_detail"
            }
        # 场景判断
        if scene == "product_search":
            keyword = self._extract_keyword(question)
            if not keyword:
                return {
                    "answer": "我暂时没有识别出你想搜索的具体商品关键词，可以换成更明确的说法，比如：手机、电脑、耳机、平板。",
                    "used_tool": False,
                    "tool_name": None
                }
            # 对关键字进行灵活处理，让LLM自行提取keyword
            product_list = search_product_list_from_api(
                category_id=1,
                keyword=keyword,
                min_price=0,
                max_price=999999,
                page_num=1,
                page_size=5,
                sort_by="price_asc"
            )

            prompt = self._build_product_search_prompt(question, product_list,user_context)

            answer = chat_with_llm(prompt)

            self.memory.add_user_message(question)
            self.memory.add_assistant_message(answer)

            return {
                "answer": answer,
                "used_tool": True,
                "tool_name": "search_product_list"
            }

        decision = self._decide_tool(question_with_memory)

        if decision.get("use_tool"):
            tool_name = decision.get("tool_name")
            arguments = decision.get("arguments", {})

            if tool_name == "search_product":
                keyword = arguments.get("keyword", question)
                tool_result = search_product(keyword, use_api=False)

                prompt = self._build_tool_prompt(question_with_memory, tool_result)
                answer = chat_with_llm(prompt)

                self.memory.add_user_message(question)
                self.memory.add_assistant_message(answer)

                return {
                    "answer": answer,
                    "used_tool": True,
                    "tool_name": "search_product",
                }

        answer = chat_with_llm(question_with_memory)

        self.memory.add_user_message(question)
        self.memory.add_assistant_message(answer)

        return {
            "answer": answer,
            "used_tool": False,
            "tool_name": None,
        }

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
    # 新增商品详情 Prompt 方法
    def _build_product_detail_prompt(self, question: str, product_detail: str) -> str:
        return f"""
        用户问题：
        {question}
    
        以下是从 UnSky Market 查询到的真实商品详情：
        {product_detail}
    
        请你基于以上真实商品信息回答用户问题。
        可以从价格、成色、描述、收藏数、浏览量等角度进行分析。
        如果信息不足，请明确说明，不要编造不存在的信息。
        """

    # 增强skybot对相应商品的分析能力
    def _build_product_analysis_prompt(self, question: str, product_detail: str) -> str:
        return f"""
        你是 Skybot，二手交易平台 UnSky Market 的智能商品分析助手。
    
        用户的问题：
        {question}
    
        以下是商品详情数据：
        {product_detail}
    
        请你基于商品真实数据进行分析，不要编造不存在的信息。
    
        请按照以下结构回答：
        1. 商品基本情况
        2. 价格是否合理
        3. 成色和描述风险
        4. 适合什么人购买
        5. 最终购买建议
    
        要求：
        - 语气自然，像平台里的 AI 助手
        - 如果数据不足，要明确说明
        - 不要承诺交易安全
        - 不要替卖家做保证
        """

    # 新增商品查询提示词，返回满足用户描述的相关搜索商品(and 用户上下文)
    def _build_product_search_prompt(
            self,
            question: str,
            product_list: str,
            user_context: dict | None = None
    ) -> str:
        user_context_text = self._build_user_context_text(user_context)

        return f"""
        你是 Skybot，二手交易平台 UnSky Market 的智能商品推荐助手。
    
        当前用户信息：
        {user_context_text}
    
        用户的问题：
        {question}
    
        以下是从平台商品列表接口查询到的商品数据：
        {product_list}
    
        请你基于真实商品数据和当前用户信息进行推荐，不要编造不存在的商品。
    
        请按照以下结构回答：
        1. 搜索结果概况
        2. 推荐商品
        3. 推荐理由
        4. 购买提醒
    
        要求：
        - 如果商品数量较少，要明确说明
        - 不要承诺交易安全
        - 不要编造价格、成色、卖家信息
        - 如果用户信息不足，只基于商品信息推荐
        """

    # 让LLM对用户的提问进行简单的解析，提出关键词
    def _extract_keyword(self, question: str) -> str:
        if "手机" in question:
            return "手机"
        if "电脑" in question:
            return "电脑"
        if "耳机" in question:
            return "耳机"
        if "平板" in question:
            return "平板"
        return ""

    # 创建用户上下文格式化方法
    def _build_user_context_text(self, user_context: dict | None) -> str:
        if not user_context:
            return "暂无用户上下文信息。"

        nickname = user_context.get("nickname") or "未设置"
        school = user_context.get("school") or "未设置"
        auth_status = user_context.get("authStatus")
        credit_score = user_context.get("creditScore")

        return (
            f"用户昵称：{nickname}\n"
            f"学校：{school}\n"
            f"认证状态：{auth_status}\n"
            f"信用分：{credit_score}"
        )