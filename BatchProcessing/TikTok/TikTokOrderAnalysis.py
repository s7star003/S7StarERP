import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
import time
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'S7starERPDjango.settings')
import django
django.setup()

# 依赖Django的模块在此之后导入
# 你的分析逻辑不直接依赖tiktok_api，但如有需要可在此处导入

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_FILE = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "tiktok_orders.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Tiktok", "OrderAnalysis.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# 需要统计的字段
FIELDS = [
    "product_name",
    "sale_price",
    "original_shipping_fee",
    "original_total_product_price",
    "total_amount",
    "sku_image"
]

RETURN_STATUS = [
    "CANCELLED", "RETURNED", "REFUNDED", "CANCELLED_AFTER_SHIPPING",
    "RETURN_REQUESTED", "CANCELLED_BY_SELLER", "CANCELLED_BY_BUYER"
]

def extract_products(obj, products, context=None, all_candidates=None):
    """
    递归遍历obj，找到包含product_name的dict，合并上下文金额字段，加入products列表。
    all_candidates用于补全字段。
    """
    if context is None:
        context = {}
    if all_candidates is None:
        all_candidates = []

    if isinstance(obj, dict):
        # 更新上下文
        new_context = context.copy()
        for field in FIELDS:
            if field in obj and obj[field] is not None:
                new_context[field] = obj[field]
        # 如果当前dict包含product_name，认为是一个商品
        if "product_name" in obj:
            product = {field: new_context.get(field) for field in FIELDS}
            # 尝试补全缺失字段
            for field in FIELDS:
                if product[field] is None:
                    for candidate in all_candidates:
                        if candidate.get(field) is not None:
                            product[field] = candidate[field]
                            break
            products.append(product)
        # 递归遍历所有子项
        for v in obj.values():
            extract_products(v, products, new_context, all_candidates + [obj])
    elif isinstance(obj, list):
        for item in obj:
            extract_products(item, products, context, all_candidates)

def analyze_orders():
    # 每次分析前清空输出文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
    except Exception as e:
        print(f"读取{INPUT_FILE}失败: {e}")
        return

    all_status = set()
    for order in orders:
        for item in order.get("line_items", []):
            all_status.add(str(item.get("display_status", "")).upper())
    print("所有出现过的display_status：", all_status)

    result = {}
    for order in orders:
        payment = order.get("payment", {})
        order_id = order.get("id")
        buyer_id = order.get("user_id")
        order_time = order.get("create_time")
        shipping_provider_name = order.get("shipping_provider_name", None)
        line_items = order.get("line_items", [])
        order_status = str(order.get("status", "")).upper()
        for item in line_items:
            product_name = item.get("product_name", "未知商品")
            if not product_name:
                continue
            sale_price = float(item.get("sale_price", 0))
            sku_name = item.get("sku_name", "未知SKU")
            sku_image = item.get("sku_image")
            # 只用订单级别status判断退货
            is_returned = order_status in RETURN_STATUS
            item_shipping_provider = item.get("shipping_provider_name", shipping_provider_name)
            # 初始化
            if product_name not in result:
                result[product_name] = {
                    "product_name": product_name,
                    "sku_image": sku_image,
                    "sell_count": 0,
                    "total_sale_amount": 0,
                    "total_order_count": set(),
                    "sale_prices": [],
                    "buyer_ids": set(),
                    "sku_list": set(),  # 这里存sku_name
                    "shipping_provider_names": set(),
                    "first_sold_time": order_time,
                    "last_sold_time": order_time,
                    "return_count": 0
                }
            result[product_name]["sell_count"] += 1
            result[product_name]["total_sale_amount"] += sale_price
            result[product_name]["total_order_count"].add(order_id)
            result[product_name]["sale_prices"].append(sale_price)
            result[product_name]["buyer_ids"].add(buyer_id)
            if sku_name:
                result[product_name]["sku_list"].add(sku_name)
            if item_shipping_provider:
                result[product_name]["shipping_provider_names"].add(item_shipping_provider)
            if is_returned:
                result[product_name]["return_count"] += 1
            if order_time:
                if result[product_name]["first_sold_time"] is None or order_time < result[product_name]["first_sold_time"]:
                    result[product_name]["first_sold_time"] = order_time
                if result[product_name]["last_sold_time"] is None or order_time > result[product_name]["last_sold_time"]:
                    result[product_name]["last_sold_time"] = order_time
            # 增加毛利统计
            profit_methods = {}
            profit_explain = {}
            # 1. 实际付款价格
            pay_price = float(item.get("sale_price", 0) or 0)
            # 2. 运费
            shipping_fee = float(item.get("original_shipping_fee") or item.get("shipping_fee") or 0)
            # 3. 平台提点（5%）
            platform_fee = pay_price * 0.05
            # 4. 货品成本
            cost = float(item.get("cost") or item.get("product_cost") or item.get("item_cost") or 0)
            # 5. 计算毛利
            profit = pay_price - shipping_fee - platform_fee - cost
            profit_methods["pay-shipping-5%-cost"] = profit
            profit_explain["pay-shipping-5%-cost"] = "毛利=实际付款（sale_price）-运费（original_shipping_fee/shipping_fee）-平台提点5%-货品成本（cost/product_cost/item_cost），本项为所有订单累计总和"
            # 可扩展更多算法
            if "profit_methods" not in result[product_name]:
                result[product_name]["profit_methods"] = defaultdict(float)
                result[product_name]["profit_explain"] = {}
            result[product_name]["profit_methods"]["pay-shipping-5%-cost"] += profit
            result[product_name]["profit_explain"].update(profit_explain)
    # 整理输出
    analysis_list = []
    for product_name, data in result.items():
        return_rate = round((data["return_count"] / data["sell_count"] * 100) if data["sell_count"] else 0, 2)
        is_returned = data["return_count"] > 0
        profit_methods = {k: round(v,2) for k,v in data.get("profit_methods",{}).items()} if not is_returned else {}
        profit_explain = data.get("profit_explain",{}) if not is_returned else {}
        analysis_list.append({
            "product_name": data["product_name"],
            "sku_image": data["sku_image"],
            "sell_count": data["sell_count"],
            "total_sale_amount": round(data["total_sale_amount"], 2),
            "total_order_count": len(data["total_order_count"]),
            "avg_sale_price": round(sum(data["sale_prices"]) / len(data["sale_prices"]) if data["sale_prices"] else 0, 2),
            "min_sale_price": round(min(data["sale_prices"]) if data["sale_prices"] else 0, 2),
            "max_sale_price": round(max(data["sale_prices"]) if data["sale_prices"] else 0, 2),
            "buyer_count": len(data["buyer_ids"]),
            "sku_list": list(data["sku_list"]),
            "shipping_provider_names": list(data["shipping_provider_names"]),
            "first_sold_time": data["first_sold_time"],
            "last_sold_time": data["last_sold_time"],
            "return_count": data["return_count"],
            "return_rate": return_rate,
            "is_returned": is_returned,
            "profit_methods": profit_methods,
            "profit_explain": profit_explain
        })
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis_list, f, ensure_ascii=False, indent=2)
    print(f"分析完成，结果已保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_orders() 