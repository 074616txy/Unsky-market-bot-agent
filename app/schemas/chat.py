from pydantic import BaseModel
from typing import Optional

# 定义请求和响应模型---规定 /chat 接口接收什么、返回什么。

# 请求与返回体都由pydantic自动检查后返回，省去抛异常的代码
class ChatRequest(BaseModel):
    user_id: Optional[int] = None
    question: str
    scene: Optional[str] = None
    product_id: Optional[int] = None
    user_context: dict | None = None


class ChatResponse(BaseModel):
    answer: str
    used_tool: bool = False
    tool_name: Optional[str] = None
# 客户端
#    ↓
# ChatRequest
#    ↓
# 业务逻辑（Agent）
#    ↓
# ChatResponse
#    ↓
# 客户端