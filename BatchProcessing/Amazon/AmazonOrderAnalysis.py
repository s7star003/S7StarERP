import json
import os
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "AmazonDatas", "Amazon_orders.json")
ORDER_ITEMS_FILE = os.path.join(PROJECT_ROOT, "Datas", "AmazonDatas", "Amazon_order_items.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Amazon", "OrderAnalysis.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

RETURN_STATUS = ["canceled", "returned", "refunded"]

def analyze_orders():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith('{'):
                orders = [json.loads(content)]
            else:
                orders = json.loads(content)
        with open(ORDER_ITEMS_FILE, "r", encoding="utf-8") as f:
            order_items_data = json.load(f)
            order_items = []
            if "OrderItems" in order_items_data:
                for item in order_items_data["OrderItems"]:
                    item["AmazonOrderId"] = order_items_data.get("AmazonOrderId")
                    order_items.append(item)
    except Exception as e:
        print(f"读取订单数据失败: {e}")
        return

    order_items_map = defaultdict(list)
    for item in order_items:
        order_id = item.get("AmazonOrderId")
        order_items_map[order_id].append(item)

    print("orders:", orders)
    print("order_items:", order_items)
    print("order_items_map:", order_items_map)

    result = {}
    for order in orders:
        order_id = order.get("AmazonOrderId")
        buyer_info = order.get("BuyerInfo", {})
        buyer_id = buyer_info.get("BuyerEmail") or buyer_info.get("BuyerName") or order_id
        order_time = order.get("PurchaseDate") or order.get("LastUpdateDate")
        shipping_provider = order.get("ShipmentServiceLevelCategory", None)
        items = order_items_map.get(order_id, [])
        print(f"order_id={order_id} items={items}")
        for item in items:
            product_name = item.get("Title", "未知商品")
            if not product_name:
                continue
            sale_price = float(item.get("ItemPrice", {}).get("Amount", 0))
            sku = item.get("ASIN") or item.get("OrderItemId") or item.get("SellerSKU")
            sku_image = item.get("ImageUrl", "")
            is_returned = str(item.get("OrderStatus", "")).lower() in RETURN_STATUS
            item_shipping_provider = shipping_provider
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
            if sku:
                result[product_name]["sku_list"].add(sku)
            if item_shipping_provider:
                result[product_name]["shipping_provider_names"].add(item_shipping_provider)
            if is_returned:
                result[product_name]["return_count"] += 1
            if order_time:
                if result[product_name]["first_sold_time"] is None or order_time < result[product_name]["first_sold_time"]:
                    result[product_name]["first_sold_time"] = order_time
                if result[product_name]["last_sold_time"] is None or order_time > result[product_name]["last_sold_time"]:
                    result[product_name]["last_sold_time"] = order_time
            profit_methods = {}
            profit_explain = {}
            pay_price = sale_price
            shipping_fee = float(item.get("ShippingPrice", {}).get("Amount", 0))
            platform_fee = pay_price * 0.05
            cost = float(item.get("ItemCost", 0))
            profit = pay_price - shipping_fee - platform_fee - cost
            profit_methods["pay-shipping-5%-cost"] = profit
            profit_explain["pay-shipping-5%-cost"] = "毛利=实际付款（ItemPrice.Amount）-运费（ShippingPrice.Amount）-平台提点5%-货品成本（ItemCost），本项为所有订单累计总和"
            if "profit_methods" not in result[product_name]:
                result[product_name]["profit_methods"] = defaultdict(float)
                result[product_name]["profit_explain"] = {}
            result[product_name]["profit_methods"]["pay-shipping-5%-cost"] += profit
            result[product_name]["profit_explain"].update(profit_explain)
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