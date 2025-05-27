import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
import json
import time
from Tiktok_api.Orders.getPriceDetail import get_price_detail

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_FILE = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "tiktok_orders.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "OrdersPriceDetail.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def batch_get_order_price_detail():
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        orders = json.load(f)
    results = []
    for order in orders:
        order_id = order.get("id")
        if not order_id:
            continue
        print(f"正在处理订单: {order_id}")
        detail = get_price_detail(order_id)
        print(f"订单: {order_id} 返回: {json.dumps(detail, ensure_ascii=False)[:200]}")  # 打印前200字符
        results.append({"order_id": order_id, "price_detail": detail})
        time.sleep(0.2)  # 防止请求过快被限流
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"已保存所有订单价格明细到 {OUTPUT_FILE}")

if __name__ == "__main__":
    batch_get_order_price_detail() 