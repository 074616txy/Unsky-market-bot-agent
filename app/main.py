from fastapi import FastAPI

from app.agents.skybot import Skybot
from app.schemas.chat import ChatRequest, ChatResponse

# 写FastAPI入口：把 Skybot 暴露成 HTTP 接口，方便 Java 后端以后调用。

app = FastAPI(title="Skybot Agent")

# 根据Skybot模板实例化一个skyron机器人对象
skybot = Skybot()


@app.get("/")
def root():
    return {"message": "Skybot is running"}


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
