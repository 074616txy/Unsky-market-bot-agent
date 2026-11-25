from fastapi import FastAPI

from app.agents.unsky_market_bot import UnskyMarketBot
from app.schemas.chat import ChatRequest, ChatResponse

# 写FastAPI入口：把 Unsky-market-bot 暴露成 HTTP 接口，方便 Java 后端以后调用。

app = FastAPI(title="Unsky-market-bot Agent")

# 根据 Unsky-market-bot 模板实例化机器人对象
unsky_market_bot = UnskyMarketBot()


@app.get("/")
def root():
    return {"message": "Unsky-market-bot is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = unsky_market_bot.chat(
        question=request.question,
        user_id=request.user_id,
        scene=request.scene,
        product_id=request.product_id,
        user_context=request.user_context
    )

    return ChatResponse(
        answer=result["answer"],
        used_tool=result["used_tool"],
        tool_name=result["tool_name"],
    )
