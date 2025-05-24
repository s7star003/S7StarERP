import os
import json
import time
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "tiktok_orders.json")
PRICE_DETAIL_FILE = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "OrdersPriceDetail.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Tiktok")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取数据
with open(ORDERS_FILE, "r", encoding="utf-8") as f:
    orders = json.load(f)
print("orders前3条id：", [str(order.get("id")) for order in orders[:3]])

with open(PRICE_DETAIL_FILE, "r", encoding="utf-8") as f:
    price_details_raw = json.load(f)
print("price_details前3条order_id：", [str(item.get("order_id")) for item in price_details_raw[:3]])

price_details = {str(item["order_id"]): item["price_detail"] for item in price_details_raw}

# 合并数据
order_map = {}
for order in orders:
    order_id = str(order.get("id"))
    if not order_id:
        continue
    detail = price_details.get(order_id, {})
    order_map[order_id] = {**order, **{"price_detail": detail}}

print("合并后订单数：", len(order_map))
print("合并后订单样例：", list(order_map.values())[:2])

# 构建sku_name_map和sku_image_map，供所有分析函数使用
sku_name_map = {}
sku_image_map = {}
for order in order_map.values():
    line_items = order.get("line_items", [])
    for item in line_items:
        sku = item.get("sku_id") or item.get("seller_sku") or item.get("product_id") or order.get("sku") or order.get("product_id") or order.get("item_id")
        if not sku:
            continue
        sku_name = item.get("sku_name") or item.get("product_name") or ""
        if sku and sku_name:
            sku_name_map[sku] = sku_name
        image = item.get("sku_image") or item.get("product_image") or ""
        if sku and image:
            sku_image_map[sku] = image

# 时间过滤工具
now = datetime.now()
def in_days(order, days):
    dt_raw = order.get("create_time") or order.get("created_at") or order.get("order_time")
    if not dt_raw:
        return False
    try:
        # 统一转为字符串再转为int，确保无论原始类型都能正确处理
        dt_str = str(dt_raw)
        if dt_str.isdigit():
            dt = datetime.fromtimestamp(int(dt_str))
        else:
            # 兼容ISO格式或常规字符串
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if 'T' in dt_str else datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return (now - dt).days < days and (now - dt).days >= 0
    except Exception as e:
        print(f"时间解析异常: {dt_raw}, 错误: {e}")
        return False

def get_sku(order):
    # 优先从line_items里取sku_id或seller_sku
    if order.get("line_items") and len(order["line_items"]) > 0:
        item = order["line_items"][0]
        return item.get("sku_id") or item.get("seller_sku") or item.get("product_id")
    return order.get("sku") or order.get("product_id") or order.get("item_id")

def get_area(order):
    # 优先从recipient_address.district_info中找autonomous community
    recipient = order.get("recipient_address", {})
    district_info = recipient.get("district_info", [])
    for d in district_info:
        if d.get("address_level_name") == "autonomous community":
            return d.get("address_name")
    # 兼容老逻辑
    return order.get("region") or order.get("area") or order.get("shipping_address", {}).get("region")

def get_buyer(order):
    return order.get("buyer_id") or order.get("user_id") or order.get("customer_id")

# 1. 销量排行榜分析（7天、30天、全部）
def sales_rank_analysis(days, filename):
    sales_counter = Counter()
    for order in order_map.values():
        sku = get_sku(order)
        if not sku:
            continue
        if days == 'all' or in_days(order, days):
            sales_counter[sku] += 1
    result = [{
        "sku": sku,
        "sku_name": sku_name_map.get(sku, ""),
        "image": sku_image_map.get(sku, ""),
        "sales": sales_counter[sku]
    } for sku in sales_counter]
    result.sort(key=lambda x: x["sales"], reverse=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(result[:20], f, ensure_ascii=False, indent=2)

sales_rank_analysis(7, "SalesRank_7d.json")
sales_rank_analysis(30, "SalesRank_30d.json")
sales_rank_analysis('all', "SalesRank_all.json")

# 2. 区域需求分布（7天、30天、全部）
def area_demand_analysis(days, filename):
    area_counter = Counter()
    area_sku_counter = defaultdict(Counter)
    for order in order_map.values():
        area = get_area(order)
        sku = get_sku(order)
        if area and sku:
            if days == 'all' or in_days(order, days):
                area_counter[area] += 1
                area_sku_counter[area][sku] += 1
    area_rank = area_counter.most_common(5)
    area_result = []
    for area, count in area_rank:
        top3 = area_sku_counter[area].most_common(3)
        area_result.append({
            "area": area,
            "sales": count,
            "top3_sku": [
                {
                    "sku": sku,
                    "sku_name": sku_name_map.get(sku, ""),
                    "image": sku_image_map.get(sku, ""),
                    "sales": c
                } for sku, c in top3
            ]
        })
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(area_result, f, ensure_ascii=False, indent=2)

area_demand_analysis(7, "AreaDemand_7d.json")
area_demand_analysis(30, "AreaDemand_30d.json")
area_demand_analysis('all', "AreaDemand_all.json")

# 3. 复购率分析（全部）
sku_buyer = defaultdict(set)
for order in order_map.values():
    sku = get_sku(order)
    buyer = get_buyer(order)
    if sku and buyer:
        sku_buyer[sku].add(buyer)
sku_repurchase = []
for sku, buyers in sku_buyer.items():
    repurchase_users = [b for b in buyers if sum(1 for o in order_map.values() if get_buyer(o)==b and get_sku(o)==sku) > 1]
    repurchase_rate = len(repurchase_users) / len(buyers) if buyers else 0
    sku_repurchase.append({
        "sku": sku,
        "sku_name": sku_name_map.get(sku, ""),
        "image": sku_image_map.get(sku, ""),
        "repurchase_rate": round(repurchase_rate*100,2),
        "total_buyers": len(buyers),
        "repurchase_users": len(repurchase_users)
    })
sku_repurchase.sort(key=lambda x: x["repurchase_rate"], reverse=True)
with open(os.path.join(OUTPUT_DIR, "RepurchaseRate.json"), "w", encoding="utf-8") as f:
    json.dump(sku_repurchase[:10], f, ensure_ascii=False, indent=2)

# 4. 退货率分析（全部）
sku_return = defaultdict(lambda: {"total":0, "return":0, "reasons":Counter()})
for order in order_map.values():
    sku = get_sku(order)
    if not sku:
        continue
    sku_return[sku]["total"] += 1
    price_detail = order.get("price_detail", {})
    if price_detail.get("is_returned") or price_detail.get("return_reason"):
        sku_return[sku]["return"] += 1
        reason = price_detail.get("return_reason") or "未知原因"
        sku_return[sku]["reasons"][reason] += 1
sku_return_list = []
for sku, info in sku_return.items():
    rate = info["return"] / info["total"] if info["total"] else 0
    sku_return_list.append({
        "sku": sku,
        "sku_name": sku_name_map.get(sku, ""),
        "image": sku_image_map.get(sku, ""),
        "return_rate": round(rate*100,2),
        "total_orders": info["total"],
        "return_orders": info["return"],
        "reasons": info["reasons"].most_common(3)
    })
sku_return_list.sort(key=lambda x: x["return_rate"], reverse=True)
with open(os.path.join(OUTPUT_DIR, "ReturnRate.json"), "w", encoding="utf-8") as f:
    json.dump(sku_return_list[:10], f, ensure_ascii=False, indent=2)

# 5. 毛利分析（全部）
sku_profit = defaultdict(lambda: {"total_profit": 0, "total_orders": 0, "profit_methods": defaultdict(float), "profit_explain": {}})
for order in order_map.values():
    # 遍历每个订单的每个line_item
    line_items = order.get("line_items", [])
    price_detail = order.get("price_detail", {})
    price_data = price_detail.get("data", {})
    price_line_items = price_data.get("line_items", [])
    for item in line_items:
        sku = item.get("sku_id") or item.get("seller_sku") or item.get("product_id") or order.get("sku") or order.get("product_id") or order.get("item_id")
        if not sku:
            continue
        # 匹配price_detail中的line_item
        price_item = None
        for pi in price_line_items:
            if (pi.get("sku_id") and pi.get("sku_id") == sku) or (pi.get("id") and pi.get("id") == item.get("id")):
                price_item = pi
                break
        # 实际付款金额
        pay_price = 0
        if order.get('payment', {}).get('total_amount'):
            pay_price = float(order['payment']['total_amount'])
        elif price_data.get('payment'):
            pay_price = float(price_data['payment'])
        elif item.get('sale_price'):
            pay_price = float(item['sale_price'])
        elif price_data.get('sku_sale_price'):
            pay_price = float(price_data['sku_sale_price'])
        elif price_item and price_item.get('payment'):
            pay_price = float(price_item['payment'])
        # 运费
        shipping_fee = 0
        if order.get('payment', {}).get('original_shipping_fee'):
            shipping_fee = float(order['payment']['original_shipping_fee'])
        elif order.get('payment', {}).get('shipping_fee'):
            shipping_fee = float(order['payment']['shipping_fee'])
        elif price_data.get('shipping_list_price'):
            shipping_fee = float(price_data['shipping_list_price'])
        elif price_item and price_item.get('shipping_list_price'):
            shipping_fee = float(price_item['shipping_list_price'])
        # 平台提点
        platform_fee = pay_price * 0.05
        # 货品成本
        cost = 0  # 暂无
        profit = pay_price - shipping_fee - platform_fee - cost
        sku_profit[sku]["total_profit"] += profit
        sku_profit[sku]["total_orders"] += 1
        sku_profit[sku]["profit_methods"]["pay-shipping-5%-cost"] += profit
        sku_profit[sku]["profit_explain"]["pay-shipping-5%-cost"] = "毛利=实际付款（total_amount/payment/sku_sale_price）-运费（original_shipping_fee/shipping_fee/shipping_list_price）-平台提点5%-货品成本（cost=0），本项为所有订单累计总和"

sku_profit_list = []
for sku, info in sku_profit.items():
    avg_profit = info["total_profit"] / info["total_orders"] if info["total_orders"] else 0
    sku_profit_list.append({
        "sku": sku,
        "sku_name": sku_name_map.get(sku, ""),
        "image": sku_image_map.get(sku, ""),
        "total_profit": round(info["total_profit"],2),
        "avg_profit": round(avg_profit,2),
        "total_orders": info["total_orders"],
        "profit_methods": {k: round(v,2) for k,v in info["profit_methods"].items()},
        "profit_explain": info["profit_explain"]
    })
with open(os.path.join(OUTPUT_DIR, "ProfitAnalysis.json"), "w", encoding="utf-8") as f:
    json.dump(sku_profit_list, f, ensure_ascii=False, indent=2)

print("所有分析结果已输出到:", OUTPUT_DIR) 