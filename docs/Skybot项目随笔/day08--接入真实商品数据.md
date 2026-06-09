
> 日期：2026/06/9
> 目标：让skybot对接Java后端项目的真实上商品数据详情接口，实现真实环境的查询详情功能

---
## 前言

- 在前面的铺垫下，day08开始实现真正的对接真实接口，由于用户是通过与skybot进行聊天来获取商品的详情，所以这些具体对接是实现在Java后端项目中的`chat()`函数内部；在进行具体功能的编写后，用户就可以通过与skybot进行交互来获取自己想要的商品详情以及得到LLM相关合理的推荐以及理由。

**实现流程**

```
用户请求 Java /api/skybot/chat
-> Java 把 product_id 一起传给 Skybot
-> Skybot 根据 product_id 调 Java 商品详情接口
-> Java 返回真实商品详情
-> Skybot 把商品详情注入 Prompt
-> LLM 生成商品分析回答
```

1. 首先针对于商品查询详情页面，需要在skybot的商品功能模块来进行拓展对接具体接口，通过拼接url来获取Java后端商品详情接口，然后再得到一组数据信息按一定格式打包给LLM

```python
def get_product_detail_from_api(product_id: int) -> str:
    url = f"{MARKET_API_BASE_URL}/api/product/detail/{product_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"调用商品详情接口失败：{e}"
        
    result = response.json()
    
    if result.get("code") != 0:
        return f"商品详情接口返回异常：{result.get('msg')}"
        
    product = result.get("data")
    
    if not product:
        return "没有找到该商品详情。"
        
    return (
        f"商品ID：{product.get('id')}\n"
        f"标题：{product.get('title')}\n"
        f"描述：{product.get('description')}\n"
        f"价格：{product.get('price')} 元\n"
        f"原价：{product.get('originalPrice')} 元\n"
        f"分类ID：{product.get('categoryId')}\n"
        f"成色等级：{product.get('conditionLevel')}\n"
        f"浏览量：{product.get('viewCount')}\n"
        f"收藏数：{product.get('favoriteCount')}\n"
        f"商品状态：{product.get('status')}\n"
        f"创建时间：{product.get('createTime')}"
    )
```

2. 在这之后，会面临一个现实问题：用户在没有提供相关的商品具体id或者是商品大致信息，LLM不会知道具体要得到那个商品的详情，所以就需要对这种情况进行单独处理：如果请求里已经明确带了 `product_id`，就不用再让 LLM 猜要不要调工具，直接查商品详情

```python
if product_id is not None:
    product_detail = get_product_detail_from_api(product_id)
    
    prompt = self._build_product_detail_prompt(
        question=question_with_memory,
        product_detail=product_detail,
    )
    answer = chat_with_llm(prompt)
    
    self.memory.add_user_message(question)
    self.memory.add_assistant_message(answer)
    
    return {
        "answer": answer,
        "used_tool": True,
        "tool_name": "get_product_detail",
    }
```

3. 在处理完之后，我们就可以获得用户的所需要的具体商品信息，但是这只会是一组数据，我们需要将这些数据返回给LLM做自然语言的润色，所以需要新增商品详情 Prompt 方法，来进行返回结果的约束

```python
def _build_product_detail_prompt(self, question: str, product_detail: str) -> str:
    return f"""
用户问题：
{question}

以下是从 UnSky Market 查询到的真实商品详情：
{product_detail}

请你基于以上真实商品信息回答用户问题。
可以从价格、成色、描述、收藏数、浏览量等角度进行分析。
如果信息不足，请明确说明，不要编造不存在的信息。
"""
```

> 我的理解：**经过以上的处理后，这个Agent的商品详情接口已经对接成功，简单来讲就是得到Java后端的接口地址，然后在skybot里面调用这个地址实现这个功能，这样这个Agent就可以拿到相关信息，这个信息必须要有具体的商品id，所以要考虑到用户没有上传商品id的情况，Agent最后拿到的商品详情数据是简单的JSON数据格式，这样的返回给用户不合理；所以最后要准备一个Prompt提示词，带着这些数据信息返回给LLM，由LLM进行汇总润色之后在返回给用户。**

> 整体流程是：Skybot 拿到 Java 后端提供的商品详情接口地址，再根据 product_id 调用该接口获取真实商品数据。由于商品详情查询必须依赖具体商品 ID，所以需要考虑用户未传入 product_id 的情况。Agent 拿到的原始数据本质上是结构化 JSON，不能直接原样返回给用户，因此需要通过 Prompt 将商品数据和用户问题一起交给 LLM，由 LLM 进行分析、总结和自然语言表达，最终返回更适合用户阅读的结果。

## 当前结果

- 已经实现Java后端的商品详情接口与skybot的对接。
- 为后续skybot和Unsky-Market项目的完全联动奠定基础，后续会继续拓展实际功能接口对接。