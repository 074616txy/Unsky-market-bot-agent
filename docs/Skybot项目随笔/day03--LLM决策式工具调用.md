
> 日期：2026/06/6
> 目标：在day02的基础上，实现用大模型决定具体调用合理的工具

---
## 前言

- day02简单实现了用代码来固定实现规则触发式的调用Agent，简单的调用了Agent的第一个Tool；但是在日常的Agent使用中通常是由LLM来决策调用哪一个工具，怎么调用(具体函数已经完成，只是由LLM传参)，这样可以更加灵活的适配日常使用Agent的任何方面。

**实现思路**

- 关于Agent让LLM决策使用工具要定义一个函数`_decide_tool(question)`来实现，这个函数负责让 LLM 判断是否调用工具，返回对应的json格式的内容告诉Agent关于大模型的想法。

- 在Agent主逻辑中新增方法：

```python
# _decide_tool()负责让Agent寻求LLM关于工具的调用的想法与具体实施方案  
def _decide_tool(self, question: str) -> dict:  
    tool_prompt = f"""  
你是 Skybot 的工具决策模块。  
  
你需要判断用户问题是否需要调用工具。  
  
当前可用工具：  
1. search_product  
   作用：搜索二手商品模拟数据  
   参数：   - keyword: 商品关键词，例如 手机、电脑、iPhone、华为  
  
用户问题：  
{question}  
  
请严格返回 JSON，不要输出任何解释文字。  
  
如果需要调用工具，返回：  
{{  
  "use_tool": true,  
  "tool_name": "search_product",  "arguments": {{  
    "keyword": "关键词"  
  }}  
}}  
  
如果不需要调用工具，返回：  
{{  
  "use_tool": false,  
  "tool_name": null,  "arguments": {{}}  
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
```

- 新增方法后要对原来的chat()进行修改：

```python
def chat(self, question: str) -> str:
    decision = self._decide_tool(question)
    
    if decision.get("use_tool"):
        tool_name = decision.get("tool_name")
        arguments = decision.get("arguments", {})
        
        if tool_name == "search_product":
            keyword = arguments.get("keyword", question)
            tool_result = search_product_mock(keyword)
            
            prompt = self._build_tool_prompt(question, tool_result)
            return chat_with_llm(prompt)
            
    return chat_with_llm(question)
```

- 具体流程：

```
用户问题
-> _decide_tool(question)
-> LLM 返回工具决策 JSON
-> 如果 use_tool = true
-> 根据 tool_name 找工具
-> 执行 search_product_mock(keyword)
-> 把工具结果注入 prompt
-> LLM 总结回答
```

> **总体来讲，关于LLM决策式工具调用都是加入一个新的函数来由LLM对是否使用工具，使用什么工具进行总结并返回结果，Agent再根据这个结果进行代码的具体执行，最终返回出正确的结果；所以说本质上还是以给Agent增加新函数的方式来对Agent进行升级，day03基本完成。**

## 当前结果

- 已完成 LLM 决策式工具调用测试。
- 商品类问题可以由 LLM 决定调用 `search_product` 工具，并基于工具返回的数据生成回答。
- 普通聊天问题可以不调用工具，直接由 LLM 回复。