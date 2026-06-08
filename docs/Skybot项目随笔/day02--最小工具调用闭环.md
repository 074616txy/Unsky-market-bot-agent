
> 日期：2026/06/4
> 目标：Skybot可以调用第一个工具来辅助满足用户的需求，扩展Agent调用工具的能力

---
## 前言

- 在前面成功可以实现机器人聊天的功能后，接下来就需要拓展Agent的能力了；由于这个Skybot是与我的Java后端项目----Unsky Market相匹配的，这里先做一个简单的搜索二手商品信息的小工具，主要是在`tools`文件夹定义一个`product_tool`工具，在里面做与商品相关的工具。

**1.准备工作**

- day02主要是实现一个工具的调用，关于这个工具什么时候调用，怎么调用都需要有LLM根据用户的需求来判断。对于这个工具来讲，它既然是一个搜索工具，就必须需要模拟数据，我们要做一个最小工具调用的闭环，我们就需要先写入一些模拟数据来进行测试。

- 后面可以继续拓展：

```
模拟数据 -> MySQL 数据 -> Java 后端接口 -> 真实平台数据
```

**2.定义Tool函数**

- 简单定义一个`search_product_mock`根据关键词进行搜索的小工具，在这个工具里面写具体实现方法，并要考虑到 "没有找到相关商品。"的情况，最后整理标准的返回格式进行返回。

- 这个Tool工具比较简单，只是为了实现简单的调用工具闭环，后面会继续拓展工具的使用边界，也会拓展查询数据的边界。总之，我的Agent--Skybot会越来越智能。


**3.skybot接入工具**

 - 再接入工具调用前，需要区分：

```
简易版：代码判断是否调用工具
Agent版：LLM 判断是否调用工具
```

- 我们这里先完成简易版(**规则触发式工具调用 Agent**)，做一个最小工具调用闭环，也就是：如果用户问题里包含 手机 / 商品 / 推荐 / 价格，就调用商品搜索工具，后续在进行完善，升级为让 LLM 输出是否调用工具。只针对这行查询代码来进行触发Agent，先把这部分内容写死，后续在升级为LLM 决策式工具调用 Agent。
- 基本流程：

```
问题进入 Skybot
-> 先判断是否需要外部工具
-> 如果需要，就调用工具获取外部信息
-> 把“用户问题 + 工具结果”重新组织成 Prompt
-> 交给 LLM 生成最终回答
```

- 代码展示：

```python
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
```

> **Skybot 在收到用户问题后，会先尝试判断是否需要工具。如果问题涉及平台商品等外部信息，就调用对应工具获取数据；随后将工具结果和用户问题一起构造成新的 Prompt，交给 LLM 生成最终回答。这个过程本质上是把工具返回的信息注入上下文，让 LLM 基于真实数据回答，而不是直接依赖模型自身知识。**

## 当前结果

>day02成功完成最小工具调用闭环：

- 新增 `product_tool.py`
- 使用模拟商品数据测试工具能力
- 在 `Skybot.chat()` 中增加工具调用判断
- 通过 `_build_tool_prompt()` 将工具结果注入上下文
- `/chat` 接口测试成功，能基于商品数据返回推荐结果

## 下一步

- 将当前规则触发式工具调用升级为 LLM 决策式工具调用。
- 后续逐步把模拟商品数据替换为真实数据库或 Java 后端接口数据。


> **Skyron已经从简单的聊天小bot升级成可以调用简单工具的中bot了，接下来我们需要在工具模块让它可以由llm大脑进行决策调用Agent**

