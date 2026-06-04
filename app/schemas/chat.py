from pydantic import BaseModel

# 定义请求和响应模型---规定 /chat 接口接收什么、返回什么。

# 请求与返回体都由pydantic自动检查后返回，省去抛异常的代码
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str

# 客户端
#    ↓
# ChatRequest
#    ↓
# 业务逻辑（Agent）
#    ↓
# ChatResponse
#    ↓
# 客户端