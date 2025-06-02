import os
import json
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "MiraviaDatas", "Miravia_orders.json")
ORDER_ITEMS_FILE = os.path.join(PROJECT_ROOT, "Datas", "MiraviaDatas", "Miravia_order_items.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Miravia")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取数据
with open(ORDERS_FILE, "r", encoding="utf-8") as f:
    orders = json.load(f)
with open(ORDER_ITEMS_FILE, "r", encoding="utf-8") as f:
    order_items = json.load(f)

# 合并订单与明细
order_map = {}
order_items_map = defaultdict(list)
for item in order_items:
    order_id = str(item.get("order_id"))
    order_items_map[order_id].append(item)
for order in orders:
    order_id = str(order.get("order_id"))
    order_map[order_id] = {**order, **{"line_items": order_items_map.get(order_id, [])}}

# 构建sku_name_map和sku_image_map
sku_name_map = {}
sku_image_map = {}
for order in order_map.values():
    for item in order.get("line_items", []):
        sku = item.get("sku") or item.get("sku_id") or item.get("product_id")
        if not sku:
            continue
        sku_name = item.get("name") or item.get("product_id") or ""
        if sku and sku_name:
            sku_name_map[sku] = sku_name
        image = item.get("product_main_image") or ""
        if sku and image:
            sku_image_map[sku] = image

def in_days(order, days):
    now = datetime.now()
    dt_raw = order.get("created_at") or order.get("updated_at")
    if not dt_raw:
        return False
    try:
        dt_str = str(dt_raw)
        if dt_str.isdigit():
            dt = datetime.fromtimestamp(int(dt_str))
        else:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if 'T' in dt_str else datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return (now - dt).days < days and (now - dt).days >= 0
    except Exception:
        return False

def get_sku(order):
    if order.get("line_items") and len(order["line_items"]) > 0:
        item = order["line_items"][0]
        return item.get("sku") or item.get("sku_id") or item.get("product_id")
    return None

def get_area(order):
    shipping = order.get("address_shipping", {})
    return shipping.get("city") or shipping.get("address4") or shipping.get("country")

def get_buyer(order):
    if order.get("line_items") and len(order["line_items"]) > 0:
        return order["line_items"][0].get("buyer_id")
    return None

def extract_amount(order, item=None):
    # 优先用item的paid_price，否则用order的price
    if item and item.get("paid_price"):
        try:
            return float(item["paid_price"])
        except Exception:
            return 0
    try:
        return float(order.get("price", 0))
    except Exception:
        return 0

def is_valid_order(order):
    # Miravia没有明显的status，简单判断金额
    try:
        amount = float(order.get("price", 0))
        if amount == 0:
            return False
    except Exception:
        return False
    return True

# 1. 销量排行榜分析（7天、30天、全部）
def sales_rank_analysis(days, filename):
    sales_counter = Counter()
    for order in order_map.values():
        if not is_valid_order(order):
            continue
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
    area_sales_amount = Counter()
    for order in order_map.values():
        if not is_valid_order(order):
            continue
        area = get_area(order)
        sku = get_sku(order)
        if area and sku:
            if days == 'all' or in_days(order, days):
                area_counter[area] += 1
                area_sku_counter[area][sku] += 1
                amount = extract_amount(order)
                area_sales_amount[area] += amount
    area_rank = area_counter.most_common(5)
    area_result = []
    for area, count in area_rank:
        top3 = area_sku_counter[area].most_common(3)
        area_result.append({
            "area": area,
            "sales": count,
            "sales_amount": round(area_sales_amount[area], 2),
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
    if not is_valid_order(order):
        continue
    sku = get_sku(order)
    buyer = get_buyer(order)
    if sku and buyer:
        sku_buyer[sku].add(buyer)
sku_repurchase = []
for sku, buyers in sku_buyer.items():
    repurchase_users = [b for b in buyers if sum(1 for o in order_map.values() if get_buyer(o)==b and get_sku(o)==sku) > 1]
    if len(repurchase_users) == 0:
        continue
    repurchase_rate = len(repurchase_users) / len(buyers) if buyers else 0
    area_counter = Counter()
    for b in repurchase_users:
        user_orders = [o for o in order_map.values() if get_buyer(o)==b and get_sku(o)==sku]
        for o in user_orders:
            area = get_area(o)
            if area:
                area_counter[area] += 1
    area = area_counter.most_common(1)[0][0] if area_counter else None
    sku_repurchase.append({
        "sku": sku,
        "sku_name": sku_name_map.get(sku, ""),
        "image": sku_image_map.get(sku, ""),
        "repurchase_rate": round(repurchase_rate*100,2),
        "total_buyers": len(buyers),
        "repurchase_users": len(repurchase_users),
        "area": area
    })
sku_repurchase.sort(key=lambda x: x["repurchase_rate"], reverse=True)
with open(os.path.join(OUTPUT_DIR, "RepurchaseRate.json"), "w", encoding="utf-8") as f:
    json.dump(sku_repurchase[:10], f, ensure_ascii=False, indent=2)

# 4. 退货率分析（全部）
RETURN_STATUS = ["canceled", "returned", "refunded"]
sku_return = defaultdict(lambda: {"total":0, "return":0, "reasons":Counter()})
for order in order_map.values():
    for item in order.get("line_items", []):
        sku = item.get("sku") or item.get("sku_id") or item.get("product_id")
        if not sku:
            continue
        sku_return[sku]["total"] += 1
        if str(item.get("status", "")).lower() in RETURN_STATUS:
            sku_return[sku]["return"] += 1
            reason = item.get("reason") or "未知原因"
            sku_return[sku]["reasons"][reason] += 1
return_rate_list = []
for product_name, data in sku_return.items():
    sell_count = data["total"]
    return_count = data["return"]
    return_rate = round((return_count / sell_count * 100) if sell_count else 0, 2)
    sku_name = sku_name_map.get(product_name, "")
    image = sku_image_map.get(product_name, "")
    return_rate_list.append({
        "sku_id": product_name,
        "sku_name": sku_name,
        "image": image,
        "sell_count": sell_count,
        "return_count": return_count,
        "return_rate": return_rate,
        "return_reasons": dict(data["reasons"])
    })
return_rate_list.sort(key=lambda x: (x["return_count"], x["return_rate"]), reverse=True)
with open(os.path.join(OUTPUT_DIR, "ReturnRate.json"), "w", encoding="utf-8") as f:
    json.dump(return_rate_list, f, ensure_ascii=False, indent=2)

# 5. 毛利分析（全部）
sku_profit = defaultdict(lambda: {"total_profit": 0, "total_orders": 0, "profit_methods": defaultdict(float), "profit_explain": {}})
for order in order_map.values():
    if not is_valid_order(order):
        continue
    sku = get_sku(order)
    if not sku:
        continue
    pay_price = extract_amount(order)
    shipping_fee = float(order.get("shipping_fee", 0))
    profit = pay_price - shipping_fee
    sku_profit[sku]["total_profit"] += profit
    sku_profit[sku]["total_orders"] += 1
    sku_profit[sku]["profit_methods"]["paid_price-shipping_fee"] += profit
    sku_profit[sku]["profit_explain"]["paid_price-shipping_fee"] = "毛利=paid_price-shipping_fee，仅统计有price且未退单（price>0）的订单"

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
sku_profit_list.sort(key=lambda x: x["total_profit"], reverse=True)
with open(os.path.join(OUTPUT_DIR, "ProfitAnalysis.json"), "w", encoding="utf-8") as f:
    json.dump(sku_profit_list, f, ensure_ascii=False, indent=2)

# 6. 月度销量分析
monthly_stats = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "total_amount": 0, "sku_name": "", "image": "", "dates": []}))
for order in order_map.values():
    if not is_valid_order(order):
        continue
    sku = get_sku(order)
    if not sku:
        continue
    order_date = order.get('created_at') or order.get('updated_at')
    if not order_date:
        continue
    try:
        dt_str = str(order_date)
        if dt_str.isdigit():
            dt = datetime.fromtimestamp(int(dt_str))
        else:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if 'T' in dt_str else datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        month_str = dt.strftime("%Y-%m")
    except Exception:
        continue
    pay_price = extract_amount(order)
    monthly_stats[month_str][sku]["sales"] += 1
    monthly_stats[month_str][sku]["total_amount"] += pay_price
    monthly_stats[month_str][sku]["sku_name"] = sku_name_map.get(sku, "")
    monthly_stats[month_str][sku]["image"] = sku_image_map.get(sku, "")
    monthly_stats[month_str][sku]["dates"].append(order_date)
monthly_result = []
for month, sku_dict in monthly_stats.items():
    for sku, info in sku_dict.items():
        avg_price = info["total_amount"] / info["sales"] if info["sales"] else 0
        monthly_result.append({
            "month": month,
            "sku": sku,
            "sku_name": info["sku_name"],
            "image": info["image"],
            "sales": info["sales"],
            "total_amount": round(info["total_amount"], 2),
            "avg_price": round(avg_price, 2),
            "dates": info["dates"]
        })
monthly_result.sort(key=lambda x: (x["month"], -x["sales"]))
with open(os.path.join(OUTPUT_DIR, "MonthlySalesAnalysis.json"), "w", encoding="utf-8") as f:
    json.dump(monthly_result, f, ensure_ascii=False, indent=2)

print("所有Miravia分析结果已输出到:", OUTPUT_DIR) 