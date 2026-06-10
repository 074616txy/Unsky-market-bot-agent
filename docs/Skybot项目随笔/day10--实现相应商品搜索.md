
> 日期：2026/06/10
> 目标：让 Skybot 能根据用户反映的模糊特征，来给用户提供相应的商品数据。

---
## 前言

- day09我们实现了skybot针对具体商品id实现专业的分析并返回给用户，提升了这个skybot的商品分析能力；在day10我们会根据用户的自然语言描述来进行搜索合适的商品，并将商品的列表的数据润色一下并返回给用户，拓展一下skybot的服务能力。

**具体流程**

```
用户自然语言需求
-> Agent 提取搜索条件
-> 调用 /api/product/list
-> 拿到商品列表
-> LLM 总结推荐
```

- chat()代码实现

```python
if scene == "product_search":  
    keyword = self._extract_keyword(question)  
    if not keyword:  
        return {  
            "answer": "我暂时没有识别出你想搜索的具体商品关键词，可以换成更明确的说法，比如：手机、电脑、耳机、平板。",  
            "used_tool": False,  
            "tool_name": None  
        }  
    # 对关键字进行灵活处理，让LLM自行提取keyword  
    product_list = search_product_list_from_api(  
        category_id=1,  
        keyword=keyword,  
        min_price=0,  
        max_price=999999,  
        page_num=1,  
        page_size=5,  
        sort_by="price_asc"  
    )  
    prompt = self._build_product_search_prompt(question, product_list)  
    
    answer = chat_with_llm(prompt)  
    
    self.memory.add_user_message(question)  
    self.memory.add_assistant_message(answer)  
    
    return {  
        "answer": answer,  
        "used_tool": True,  
        "tool_name": "search_product_list"  
    }
```

> 目前在LLM关键词提取的方面我们是由固定模板向着这个简单关键词提取，这种方法比较死板，就是让LLM提取用户问题中的固定关键词，比如说“手机”、“学习资料”等等，这种提示词固定是在后端项目中的商品分类标签。

```python
# 让LLM对用户的提问进行简单的解析，提出关键词  
def _extract_keyword(self, question: str) -> str:  
    if "手机" in question:  
        return "手机"  
    if "电脑" in question:  
        return "电脑"  
    if "耳机" in question:  
        return "耳机"  
    if "平板" in question:  
        return "平板"  
    return ""
```

> 后续会进行相应的升级，比如说让LLM 从用户问题中提取 keyword、categoryId、价格区间、排序方式等参数，来实现更精准的查询，让skybot更好的服务用户，满足用户的需求。

**总结一下**

> **Day10 主要是在 Agent 中接入商品列表接口，让 Skybot 不只能够根据商品 ID 分析单个商品，也可以根据用户的自然语言需求搜索商品列表并进行推荐。当前实现采用规则式关键词提取，比如识别“手机、电脑、耳机、平板”等关键词，再调用 Java 后端的商品列表接口获取真实商品数据。拿到商品列表后，Agent 会通过 Prompt 将商品数据交给 LLM，由 LLM 进行总结和推荐。这个阶段的重点不是实现复杂的智能搜索，而是跑通“用户需求 -> 提取搜索条件 -> 调用商品列表接口 -> LLM 推荐”的完整链路。后续可以升级为由 LLM 自动提取关键词、分类、价格区间和排序方式。**

## 当前结果

- 已经实现skybot的商品智能搜索能力增强。
- 可以更好满足用户的需求，完善skybot的多功能智能体，拓展它的功能边界。