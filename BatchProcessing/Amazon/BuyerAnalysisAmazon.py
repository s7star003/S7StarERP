import os
import sys
import json
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "AmazonDatas", "Amazon_orders.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Amazon", "BuyerAnalysis.json")
ORDER_ITEMS_FILE = os.path.join(PROJECT_ROOT, "Datas", "AmazonDatas", "Amazon_order_items.json")

def get_order_total(order):
    if "OrderTotal" in order and order["OrderTotal"].get("Amount"):
        return float(order["OrderTotal"]["Amount"])
    total = 0
    for item in order.get("line_items", []):
        try:
            total += float(item.get("ItemPrice", {}).get("Amount", 0))
        except Exception:
            continue
    return total

def main():
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
        order_items_map = defaultdict(list)
        for item in order_items:
            order_id = item.get("AmazonOrderId")
            order_items_map[order_id].append(item)
        for order in orders:
            order_id = order.get("AmazonOrderId")
            order["line_items"] = order_items_map.get(order_id, [])
        buyer_stats = {}
        for order in orders:
            try:
                amount = get_order_total(order)
            except Exception:
                continue
            if amount == 0:
                continue
            buyer_info = order.get("BuyerInfo", {})
            buyer_id = buyer_info.get("BuyerEmail") or buyer_info.get("BuyerName") or order.get("AmazonOrderId")
            first_name = buyer_info.get("BuyerName", "")
            last_name = buyer_info.get("BuyerTaxInfo", {}).get("CompanyLegalName", "")
            if not buyer_id:
                continue
            if buyer_id not in buyer_stats:
                buyer_stats[buyer_id] = {"buyer_id": buyer_id, "order_count": 0, "total_amount": 0, "first_name": first_name, "last_name": last_name}
            buyer_stats[buyer_id]["order_count"] += 1
            buyer_stats[buyer_id]["total_amount"] += amount
        result = list(buyer_stats.values())
        result.sort(key=lambda x: (-x["total_amount"], -x["order_count"]))
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"买家分析已输出到 {OUTPUT_FILE}")
    except Exception as e:
        print(f"读取{ORDERS_FILE}失败: {e}")

if __name__ == "__main__":
    main() 