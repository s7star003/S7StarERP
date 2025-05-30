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

def extract_amount(price_detail):
    if not price_detail:
        return 0
    data = price_detail.get("data", {})
    if "payment" in data:
        try:
            return float(data["payment"])
        except Exception:
            return 0
    if "total" in data:
        try:
            return float(data["total"])
        except Exception:
            return 0
    return 0

def is_valid_order(order):
    if str(order.get("status", "")).upper() in [
        "CANCELLED", "RETURNED", "REFUNDED", "CANCELLED_AFTER_SHIPPING",
        "RETURN_REQUESTED", "CANCELLED_BY_SELLER", "CANCELLED_BY_BUYER"
    ]:
        return False
    try:
        amount = float(order.get("payment", {}).get("total_amount", 0))
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
    area_sales_amount = Counter()  # 区域销售额统计
    for order in order_map.values():
        if not is_valid_order(order):
            continue
        area = get_area(order)
        sku = get_sku(order)
        if area and sku:
            if days == 'all' or in_days(order, days):
                area_counter[area] += 1
                area_sku_counter[area][sku] += 1
                price_detail = order.get("price_detail", {})
                amount = extract_amount(price_detail)
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
    repurchase_users = [b for b in buyers if sum(1 for o in order_map.values() if get_buyer(o)==b and get_sku(o)==sku and o.get('status') != 'CANCELLED') > 1]
    if len(repurchase_users) == 0:
        continue  # 跳过没有回购用户的商品
    repurchase_rate = len(repurchase_users) / len(buyers) if buyers else 0
    # 统计复购用户的区域，取出现次数最多的区域
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
RETURN_STATUS = [
    "CANCELLED", "RETURNED", "REFUNDED", "CANCELLED_AFTER_SHIPPING",
    "RETURN_REQUESTED", "CANCELLED_BY_SELLER", "CANCELLED_BY_BUYER"
]
sku_return = defaultdict(lambda: {"total":0, "return":0, "reasons":Counter()})
for order in order_map.values():
    order_status = str(order.get("status", "")).upper()
    cancel_reason = order.get("cancel_reason", "")
    for item in order.get("line_items", []):
        sku = item.get("sku_id") or item.get("seller_sku") or item.get("product_id")
        if not sku:
            continue
        sku_return[sku]["total"] += 1
        # 只要订单是退货/取消单，就统计 cancel_reason
        if order_status in RETURN_STATUS:
            sku_return[sku]["return"] += 1
            if cancel_reason:
                sku_return[sku]["reasons"][cancel_reason] += 1
            else:
                sku_return[sku]["reasons"]["未知原因"] += 1
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
# 排序：先按退货数量降序，再按退货率降序
return_rate_list.sort(key=lambda x: (x["return_count"], x["return_rate"]), reverse=True)
with open(os.path.join(OUTPUT_DIR, "ReturnRate.json"), "w", encoding="utf-8") as f:
    json.dump(return_rate_list, f, ensure_ascii=False, indent=2)

# 5. 毛利分析（全部）
sku_profit = defaultdict(lambda: {"total_profit": 0, "total_orders": 0, "profit_methods": defaultdict(float), "profit_explain": {}})
for order in order_map.values():
    if not is_valid_order(order):
        continue
    line_items = order.get("line_items", [])
    sku = get_sku(order)
    if not sku:
        continue
    pay_price = order.get('payment', {}).get('total_amount')
    shipping_fee = order.get('payment', {}).get('original_shipping_fee')
    try:
        pay_price = float(pay_price)
        shipping_fee = float(shipping_fee)
    except Exception:
        continue
    profit = pay_price - shipping_fee
    sku_profit[sku]["total_profit"] += profit
    sku_profit[sku]["total_orders"] += 1
    sku_profit[sku]["profit_methods"]["total_amount-original_shipping_fee"] += profit
    sku_profit[sku]["profit_explain"]["total_amount-original_shipping_fee"] = "毛利=total_amount-original_shipping_fee，仅统计有total_amount且未退单（status!=CANCELLED）且total_amount>0的订单"

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
print("写入前前10条total_profit:", [x["total_profit"] for x in sku_profit_list[:10]])
with open(os.path.join(OUTPUT_DIR, "ProfitAnalysis.json"), "w", encoding="utf-8") as f:
    json.dump(sku_profit_list, f, ensure_ascii=False, indent=2)

# 新增：按月统计销量、客单价和SKU信息
monthly_stats = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "total_amount": 0, "sku_name": "", "image": "", "dates": []}))
for order in order_map.values():
    if not is_valid_order(order):
        continue
    sku = get_sku(order)
    if not sku:
        continue
    order_date = order.get('create_time') or order.get('created_at') or order.get('order_time')
    if not order_date:
        continue
    try:
        dt_str = str(order_date)
        if dt_str.isdigit():
            dt = datetime.fromtimestamp(int(dt_str))
        else:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if 'T' in dt_str else datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        month_str = dt.strftime("%Y-%m")
    except Exception as e:
        print(f"日期解析异常: {order_date}, 错误: {e}")
        continue
    pay_price = order.get('payment', {}).get('total_amount')
    try:
        pay_price = float(pay_price)
    except Exception:
        pay_price = 0
    monthly_stats[month_str][sku]["sales"] += 1
    monthly_stats[month_str][sku]["total_amount"] += pay_price
    monthly_stats[month_str][sku]["sku_name"] = sku_name_map.get(sku, "")
    monthly_stats[month_str][sku]["image"] = sku_image_map.get(sku, "")
    monthly_stats[month_str][sku]["dates"].append(order_date)
# 整理输出
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

print("所有分析结果已输出到:", OUTPUT_DIR)

# 统计销售总额与去除退单后的销售额
order_status_map = {str(order.get('id')): order.get('status') for order in orders}

# tiktok_orders.json
cancelled_count = sum(1 for order in orders if order.get('status') == 'CANCELLED')
print(f"退单（CANCELLED）订单数量: {cancelled_count}")

total_order_amount = 0
valid_order_amount = 0
for order in orders:
    try:
        amt = float(order.get('payment', {}).get('total_amount', 0))
        total_order_amount += amt
        if order.get('status') != 'CANCELLED':
            valid_order_amount += amt
    except Exception:
        pass
print(f"tiktok_orders.json总订单金额: {round(total_order_amount, 2)}")
print(f"tiktok_orders.json去除退单后的总订单金额: {round(valid_order_amount, 2)}")

# OrdersPriceDetail.json
price_detail_path = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "OrdersPriceDetail.json")
with open(price_detail_path, 'r', encoding='utf-8') as f:
    price_details = json.load(f)

total_price_detail = 0
valid_price_detail = 0
cancelled_detail_count = 0
for item in price_details:
    try:
        amt = float(item.get('price_detail', {}).get('data', {}).get('payment', 0))
        total_price_detail += amt
        order_id = str(item.get('order_id'))
        status = order_status_map.get(order_id)
        if status == 'CANCELLED':
            cancelled_detail_count += 1
        if status != 'CANCELLED':
            valid_price_detail += amt
    except Exception as e:
        print(f"调试异常: {e}")
        pass
print(f"OrdersPriceDetail.json总订单金额: {round(total_price_detail, 2)}")
print(f"OrdersPriceDetail.json去除退单后的总订单金额: {round(valid_price_detail, 2)}")
print(f"明细表中属于退单的明细数量: {cancelled_detail_count}") 