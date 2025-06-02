import json
import os
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "SheinDatas", "shein_orders.json")
ORDER_ITEMS_FILE = os.path.join(PROJECT_ROOT, "Datas", "SheinDatas", "Shein_order_details.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Shein", "OrderAnalysis.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

RETURN_STATUS = [7, 8, 9]  # 假定Shein的7/8/9为退货相关状态

def analyze_orders():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
        with open(ORDER_ITEMS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            if isinstance(raw, dict):
                raw = [raw]
            order_items = []
            for order in raw:
                order_no = order.get("orderNo")
                for good in order.get("orderGoodsInfoList", []):
                    good["orderNo"] = order_no
                    order_items.append(good)
    except Exception as e:
        print(f"读取订单数据失败: {e}")
        return

    # 构建sku_name_map，直接遍历order_items
    sku_name_map = {}
    for item in order_items:
        sku = item.get("skuCode") or item.get("goodsSn") or item.get("sellerSku")
        sku_name = item.get("goodsTitle") or sku
        if sku and sku_name:
            sku_name_map[sku] = sku_name

    # 合并订单与明细
    order_map = {}
    order_items_map = defaultdict(list)
    for item in order_items:
        order_id = str(item.get("orderNo"))
        order_items_map[order_id].append(item)
    for order in orders:
        order_id = str(order.get("orderNo"))
        order_map[order_id] = {**order, **{"line_items": order_items_map.get(order_id, [])}}

    result = {}
    for order in orders:
        order_id = str(order.get("orderNo"))
        order_time = order.get("orderCreateTime") or order.get("orderUpdateTime")
        items = order_items_map.get(order_id, [])
        for item in items:
            sku = item.get("skuCode") or item.get("goodsSn") or item.get("sellerSku")
            product_name = sku_name_map.get(sku, "")
            if not product_name:
                continue
            sale_price = float(item.get("sellerCurrencyPrice", 0))
            sku_image = item.get("spuPicURL", "")
            is_returned = int(item.get("goodsStatus", 0)) in RETURN_STATUS
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
                    "sku_list": set(),
                    "first_sold_time": order_time,
                    "last_sold_time": order_time,
                    "return_count": 0
                }
            result[product_name]["sell_count"] += 1
            result[product_name]["total_sale_amount"] += sale_price
            result[product_name]["total_order_count"].add(order_id)
            result[product_name]["sale_prices"].append(sale_price)
            result[product_name]["buyer_ids"].add(order_id)
            if sku:
                result[product_name]["sku_list"].add(sku)
            if is_returned:
                result[product_name]["return_count"] += 1
            if order_time:
                if result[product_name]["first_sold_time"] is None or order_time < result[product_name]["first_sold_time"]:
                    result[product_name]["first_sold_time"] = order_time
                if result[product_name]["last_sold_time"] is None or order_time > result[product_name]["last_sold_time"]:
                    result[product_name]["last_sold_time"] = order_time
            # 毛利统计
            profit_methods = {}
            profit_explain = {}
            pay_price = sale_price
            shipping_fee = 0
            platform_fee = pay_price * 0.08  # 假定Shein平台提点8%
            cost = float(item.get("costPrice") or 0)
            profit = pay_price - shipping_fee - platform_fee - cost
            profit_methods["pay-shipping-8%-cost"] = profit
            profit_explain["pay-shipping-8%-cost"] = "毛利=实际付款（sellerCurrencyPrice）-运费（无）-平台提点8%-货品成本（costPrice），本项为所有订单累计总和"
            if "profit_methods" not in result[product_name]:
                result[product_name]["profit_methods"] = defaultdict(float)
                result[product_name]["profit_explain"] = {}
            result[product_name]["profit_methods"]["pay-shipping-8%-cost"] += profit
            result[product_name]["profit_explain"].update(profit_explain)
    # 整理输出
    analysis_list = []
    for product_name, data in result.items():
        return_rate = round((data["return_count"] / data["sell_count"] * 100) if data["sell_count"] else 0, 2)
        is_returned = data["return_count"] > 0
        profit_methods = {k: round(v,2) for k,v in data.get("profit_methods",{}).items()} if not is_returned else {}
        profit_explain = data.get("profit_explain",{}) if not is_returned else {}
        analysis_list.append({
            "product_name": product_name,
            "sku_image": data["sku_image"],
            "sell_count": data["sell_count"],
            "total_sale_amount": round(data["total_sale_amount"], 2),
            "total_order_count": len(data["total_order_count"]),
            "avg_sale_price": round(sum(data["sale_prices"]) / len(data["sale_prices"]) if data["sale_prices"] else 0, 2),
            "min_sale_price": round(min(data["sale_prices"]) if data["sale_prices"] else 0, 2),
            "max_sale_price": round(max(data["sale_prices"]) if data["sale_prices"] else 0, 2),
            "buyer_count": len(data["buyer_ids"]),
            "sku_list": list(data["sku_list"]),
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