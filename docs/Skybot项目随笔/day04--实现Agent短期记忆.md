
> 日期：2026/06/7
> 目标：用户连续对话时，Skybot 能记住前几轮问答，并在下一次回答时参考上下文

---

## 前言

- 目前已经解决使用LLM决策式调用工具的具体操作，但是由于这个Agent没有形成记忆系统，所以它无法根据用户多轮提问实现简单的上下文记忆，在day04我们就要实现简单的记忆实现。
- 在这只专注短期记忆，所以暂时不需要将记忆内容都存储在大型数据库`MySQL`,`Redis`里面，我们需要在Agent里面的记忆模块memory里面进行简单的记忆列表存储。

**实现思路：**

1. 首先需要在记忆模块加入`SimpleMemory`用来实现短期对话记录存储

```python
class SimpleMemory:
    def __init__(self, max_rounds: int = 5):
        self.max_rounds = max_rounds
        self.messages = []
        
    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content,
        })
        self._trim()
        
    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content,
        })
        self._trim()
        
    def get_context(self) -> str:
        if not self.messages:
            return ""
            
        lines = []
        
        for message in self.messages:
            role = "用户" if message["role"] == "user" else "Skybot"
            lines.append(f"{role}: {message['content']}")
            
        return "\n".join(lines)
        
    def clear(self):
        self.messages.clear()
        
    def _trim(self):
        max_messages = self.max_rounds * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
```

2. 在 Skybot 里接入 `memory`功能，这个功能通过`import`进行导入，然后再进行初始化记忆，这样skybot就可以实现短期记忆功能

3. 修改chat逻辑，让智能体在回答问题前自动读取上下文记忆，回答问题后也要保存本轮问答的历史纪录，这里先做短期记忆，所以只需用保存五轮对话记录就可以了。

```python
def chat(self, question: str) -> str:
    memory_context = self.memory.get_context()
    
    question_with_memory = self._build_memory_prompt(question, memory_context)
    
    decision = self._decide_tool(question_with_memory)
    
    if decision.get("use_tool"):
        tool_name = decision.get("tool_name")
        arguments = decision.get("arguments", {})
        
        if tool_name == "search_product":
            keyword = arguments.get("keyword", question)
            tool_result = search_product_mock(keyword)
            
            prompt = self._build_tool_prompt(question_with_memory, tool_result)
            answer = chat_with_llm(prompt)
            
            self.memory.add_user_message(question)
            self.memory.add_assistant_message(answer)
            
            return answer
            
    answer = chat_with_llm(question_with_memory)
    
    self.memory.add_user_message(question)
    self.memory.add_assistant_message(answer)
    
    return answer
```

4. 新增记忆 Prompt 方法`_build_memory_prompt()`，用Prompt来将历史对话记录和用户回答作为上下文进行整合，实现skybot的短期记忆。

> **通过上面的具体操作成功实现了Agent的短期记忆，我测试两个有联系的问题可以经过很好的分析给出合理的答案；虽然实现了记忆系统，但这只能作为我们记忆与RAG体系学习的基础，后面会使用大型数据库和RAG向量知识库来进行记忆体系的完善。**

## 当前结果

- 已完成Agent短期记忆功能。
- 在用户聊天交互过程，Agent会自动存储最近五轮的聊天记录作为历史上下文输出给大模型。
- 为后续记忆系统的升级打下坚实的基础。
