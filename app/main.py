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
    answer = skybot.chat(request.question)
    return ChatResponse(answer=answer)
