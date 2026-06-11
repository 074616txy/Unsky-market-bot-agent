# Skybot Agent

Skybot Agent 是一个面向 UnSky Market 二手交易平台的 AI 智能助手服务。

它作为独立的 Python Agent 服务运行，通过 HTTP 接口被 Java 后端调用，为平台提供商品分析、商品推荐、用户上下文问答等能力。

## 项目定位

Skybot 不是直接嵌入 Java 后端的功能模块，而是一个独立的 AI Agent 服务。

整体调用链路：

```text
前端页面 -> Java 后端 -> Python Skybot Agent -> LLM / 工具接口 -> 返回结果
```

## 已实现功能

- 最小 Agent 问答闭环
- LLM API 接入
- 商品详情工具调用
- 商品分析能力
- 商品列表搜索与推荐
- 用户上下文注入
- 短期对话记忆
- 安全边界与业务规则约束
- 前端商品详情页 AI 分析接入

## 技术栈

- Python
- FastAPI
- Uvicorn
- Requests
- Pydantic
- LLM API
- Java 后端 HTTP 接口调用

## 项目结构

```text
skybot-agent
├── app
│   ├── agents
│   │   └── skybot.py
│   ├── core
│   │   ├── config.py
│   │   └── llm.py
│   ├── memory
│   │   └── simple_memory.py
│   ├── schemas
│   │   └── chat.py
│   ├── tools
│   │   └── product_tool.py
│   └── main.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## 核心接口

### POST /chat

请求示例：

```json
{
  "user_id": 29,
  "question": "帮我分析一下这个商品值不值得买",
  "scene": "product_analysis",
  "product_id": 1,
  "user_context": {
    "authStatus": 0,
    "creditScore": 100
  }
}
```

响应示例：

```json
{
  "answer": "该商品价格偏高，建议结合成色、描述和卖家信息进一步判断。",
  "used_tool": true,
  "tool_name": "get_product_detail"
}
```

## 支持场景

### 商品详情分析

通过 `product_id` 调用 Java 后端商品详情接口，获取真实商品数据，再由 LLM 生成分析结果。

适用场景：

```text
帮我分析这个商品值不值得买
这个商品有什么风险
这个价格合理吗
```

### 商品搜索推荐

根据用户问题提取关键词，调用 Java 后端商品列表接口，获取商品列表后由 LLM 进行推荐。

适用场景：

```text
有没有便宜点的手机推荐
帮我找一些电脑
推荐几个适合买的商品
```

### 用户上下文问答

请求中可以携带 `user_context`，让 Skybot 在回答时参考当前用户信息。

目前支持字段示例：

```json
{
  "nickname": null,
  "school": null,
  "authStatus": 0,
  "creditScore": 100
}
```

## 环境变量

请在项目根目录创建 `.env` 文件：

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url
LLM_MODEL=your_model_name
MARKET_API_BASE_URL=http://localhost:8081
```

不要将真实 `.env` 文件提交到 GitHub。

## 启动方式

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务：

```bash
uvicorn app.main:app --reload
```

默认服务地址：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 与 UnSky Market 的关系

UnSky Market Java 后端负责真实业务逻辑和数据管理。

Skybot Agent 负责理解用户问题、调用工具接口、组织上下文并生成自然语言回答。

两者通过 HTTP 通信：

```text
Java 后端调用 Python Agent 的 /chat 接口
Python Agent 根据需要调用 Java 后端的商品接口
```

## 当前限制

- 目前记忆系统是简单短期记忆，还没有接入数据库或 Redis
- 商品搜索关键词提取仍是规则版本，后续可以升级为 LLM 参数提取
- 前端 AI 窗口和 UI 还处于初步接入阶段
- 暂未实现流式输出
- 暂未进行 Docker 和服务器部署

## 后续计划

- 优化全站 AI 助手窗口
- 接入持久化记忆
- 使用 LLM 提取搜索参数
- 增加更多业务工具
- 支持流式回答
- 完成 Docker / 服务器部署