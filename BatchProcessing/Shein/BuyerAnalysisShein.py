import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "SheinDatas", "shein_orders.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "MultiplatformDataDashboardDataSource", "Shein", "BuyerAnalysis.json")

def main():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
        # 买家分析统计逻辑
        buyer_stats = {}
        for order in orders:
            try:
                amount = float(order.get("productTotalPrice", 0))
            except Exception:
                continue
            if amount == 0:
                continue
            buyer_id = order.get("orderNo")  # Shein无买家唯一ID，暂用订单号
            if not buyer_id:
                continue
            if buyer_id not in buyer_stats:
                buyer_stats[buyer_id] = {"buyer_id": buyer_id, "order_count": 0, "total_amount": 0}
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