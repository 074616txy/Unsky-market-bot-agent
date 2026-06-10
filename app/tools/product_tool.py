import requests

from app.core.config import MARKET_API_BASE_URL
# 实现skybot工具调用的最小闭环，让skybot能够简单的调用搜索商品的工具

# 准备模拟数据测试工具的调用是否成功
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "iPhone 13",
        "price": 2300,
        "condition": "9成新",
        "category": "手机",
        "description": "电池健康 88%，无拆修，适合日常使用",
    },
    {
        "id": 2,
        "name": "华为 Mate 60",
        "price": 3200,
        "condition": "8成新",
        "category": "手机",
        "description": "国产旗舰，支持卫星通信，外观轻微划痕",
    },
    {
        "id": 3,
        "name": "MacBook Air M1",
        "price": 3900,
        "condition": "95新",
        "category": "电脑",
        "description": "轻薄办公本，续航优秀，适合学生和办公",
    },
]

# 定义搜索模拟二手商品的函数
# 用关键词在模拟商品里搜索，并返回文本结果
def search_product_mock(keyword: str) -> str:
    matched_products = [] # 存放搜索结果

    for product in MOCK_PRODUCTS:
        if (
            keyword in product["name"]
            or keyword in product["category"]
            or keyword in product["description"]
        ):
            matched_products.append(product)

    if not matched_products:
        return "没有找到相关商品。"

    result_lines = [] # 存放最终输出文本

    # 整理最后返回格式
    for product in matched_products:
        result_lines.append(
            f"商品ID：{product['id']}\n"
            f"名称：{product['name']}\n"
            f"价格：{product['price']} 元\n"
            f"成色：{product['condition']}\n"
            f"描述：{product['description']}"
        )

    return "\n\n".join(result_lines) # 返回时把多个商品拼成一个字符串

# 预留接口工具
def search_product_from_api(keyword: str) -> str:
    url = f"{MARKET_API_BASE_URL}/api/products/search"

    try:
        response = requests.get(
            url,
            params={"keyword": keyword},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"调用商品接口失败：{e}"

    products = response.json()

    if not products:
        return "没有找到相关商品。"

    result_lines = []

    for product in products:
        result_lines.append(
            f"商品ID：{product.get('id')}\n"
            f"名称：{product.get('name')}\n"
            f"价格：{product.get('price')} 元\n"
            f"成色：{product.get('condition', '未知')}\n"
            f"描述：{product.get('description', '暂无描述')}"
        )

    return "\n\n".join(result_lines)

# 加一个统一工具入口,方便以后进行切换
def search_product(keyword: str, use_api: bool = False) -> str:
    if use_api:
        return search_product_from_api(keyword)

    return search_product_mock(keyword)

# 获取商品详情接口的函数，对接Java后端具体商品详情数据
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

# 根据用户自然语言描述来搜索相关商品列表
def search_product_list_from_api(
    category_id: int = 1,
    keyword: str = "",
    min_price: int = 0,
    max_price: int = 999999,
    page_num: int = 1,
    page_size: int = 5,
    sort_by: str = "price_asc"
) -> str:
    url = f"{MARKET_API_BASE_URL}/api/product/list"

    params = {
        "categoryId": category_id,
        "keyword": keyword,
        "minPrice": min_price,
        "maxPrice": max_price,
        "pageNum": page_num,
        "pageSize": page_size,
        "sortBy": sort_by
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    result = response.json()

    if result.get("code") != 0:
        return f"商品列表接口返回异常：{result.get('msg')}"

    data = result.get("data") or {}
    records = data.get("records") or []

    if not records:
        return "没有搜索到符合条件的商品。"

    lines = []
    for product in records:
        lines.append(
            f"商品ID：{product.get('id')}\n"
            f"标题：{product.get('title')}\n"
            f"描述：{product.get('description')}\n"
            f"价格：{product.get('price')} 元\n"
            f"原价：{product.get('originalPrice')} 元\n"
            f"成色等级：{product.get('conditionLevel')}\n"
            f"浏览量：{product.get('viewCount')}\n"
            f"收藏数：{product.get('favoriteCount')}\n"
        )

    return "\n---\n".join(lines)