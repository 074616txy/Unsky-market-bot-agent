
> 日期：2026/06/8
> 目标：设计并测试 Java 项目如何调用 Python Agent 服务

---
## 前言

- 实现 Java 项目与Python Agent 服务接口的契约，就要配置一下chat所返回的和接收的信息格式，要具体一定要求，最终要达到让 Skybot 的 /chat 接口更适合被 Java 后端调用。

**具体操作**

1. 修改 `ChatRequest`和 `ChatResponse`，将返回和请求的格式改成标准格式

```python
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: Optional[int] = None # 哪个用户在问，后面做记忆和用户画像会用
    question: str # 用户问题
    scene: Optional[str] = None # 当前场景，比如商品推荐、客服问答、平台规则
    product_id: Optional[int] = None # 当前商品ID，后面做商品详情分析会用
    
class ChatResponse(BaseModel):
    answer: str # 用户回答
    used_tool: bool = False # 是否调用工具
    tool_name: Optional[str] = None # 调用工具的名称
```

2. 让 Skybot.chat 返回更多信息，让Skybot返回一个字典包含更多的信息

```python
def chat(
    self,
    question: str,
    user_id: int | None = None,
    scene: str | None = None,
    product_id: int | None = None,
) -> dict:
    decision = self._decide_tool(question)
    
    if decision.get("use_tool"):
        tool_name = decision.get("tool_name")
        arguments = decision.get("arguments", {})
        
        if tool_name == "search_product":
            keyword = arguments.get("keyword", question)
            tool_result = search_product(keyword, use_api=False)
            
            prompt = self._build_tool_prompt(question, tool_result)
            answer = chat_with_llm(prompt)
            
            return {
                "answer": answer,
                "used_tool": True,
                "tool_name": "search_product",
            }
    answer = chat_with_llm(question)
    
    return {
        "answer": answer,
        "used_tool": False,
        "tool_name": None,
    }
```

3. 修改 main.py，补充对应chat接口的返回和请求格式

```python
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = skybot.chat(
        question=request.question,
        user_id=request.user_id,
        scene=request.scene,
        product_id=request.product_id,
    )
    return ChatResponse(
        answer=result["answer"],
        used_tool=result["used_tool"],
        tool_name=result["tool_name"],
    )
```

- 当前chat()逻辑：

```
读取短期记忆
-> 构造带历史的问题
-> 让 LLM 决策是否调用工具
-> 执行工具或普通回答
-> 保存本轮对话
-> 返回 Java 友好的结构化响应
```

> **总体来讲，上述代码就是简单修改了请求体和返回体的格式，因为这个Agent可能会接收多个用户的提问回答，所以肯定要有user_id来进行用户隔离等，在进行格式的确定后就会更加适配真是的工作环境以及后端项目场景，现在已经将 Skybot /chat 接口升级为面向 Java 后端调用的结构化接口，并保留短期记忆与工具调用能力。这个Skybot正在一步步地升级。**

## 当前结果

- 已确定Agent请求体和返回体的格式标准。
- 为后续skybot和Unsky-Market项目的联动实现接口的完整契约。