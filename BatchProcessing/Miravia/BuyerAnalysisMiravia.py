import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "MiraviaDatas", "Miravia_orders.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Miravia", "BuyerAnalysis.json")

def main():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
        # 买家分析统计逻辑
        buyer_stats = {}
        for order in orders:
            # Miravia无明显status，金额为0视为无效
            try:
                amount = float(order.get("price", 0))
            except Exception:
                continue
            if amount == 0:
                continue
            buyer_id = order.get("customer_last_name") + order.get("customer_first_name") if order.get("customer_first_name") else None
            if not buyer_id:
                buyer_id = order.get("order_id")  # 兜底唯一
            first_name = order.get("customer_first_name") or order.get("address_shipping", {}).get("first_name", "")
            last_name = order.get("customer_last_name") or order.get("address_shipping", {}).get("last_name", "")
            if not buyer_id:
                continue
            if buyer_id not in buyer_stats:
                buyer_stats[buyer_id] = {"buyer_id": buyer_id, "order_count": 0, "total_amount": 0, "first_name": first_name, "last_name": last_name}
            buyer_stats[buyer_id]["order_count"] += 1
            buyer_stats[buyer_id]["total_amount"] += amount
        result = list(buyer_stats.values())
        # 先按total_amount降序，再按order_count降序排序
        result.sort(key=lambda x: (-x["total_amount"], -x["order_count"]))
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"买家分析已输出到 {OUTPUT_FILE}")
    except Exception as e:
        print(f"读取{ORDERS_FILE}失败: {e}")

if __name__ == "__main__":
    main() 