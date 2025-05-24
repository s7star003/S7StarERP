import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'S7starERPDjango.settings')
import django
django.setup()

# 这里再导入依赖Django的模块
from Tiktok_api.Orders.get_order_list import get_order_list
import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "tiktok_orders.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
PAGE_SIZE = 100

INPUT_URL = "你的API请求地址"  # 这里请替换为实际API调用


def fetch_orders(next_page_token=None):
    resp_text = get_order_list(PAGE_SIZE, next_page_token)
    resp_json = json.loads(resp_text)
    return resp_json


def sync_orders():
    total_count = None
    synced_count = 0
    next_page_token = None
    order_dict = {}

    while True:
        data = fetch_orders(next_page_token)
        orders = data.get("data", {}).get("orders", [])
        new_next_page_token = data.get("data", {}).get("next_page_token")
        total_count = data.get("data", {}).get("total_count", len(order_dict) + len(orders))

        for order in orders:
            order_id = order.get("id")
            if order_id:
                order_dict[order_id] = order  # 后出现的会覆盖前面的
        synced_count = len(order_dict)
        print(f"已同步 {synced_count}/{total_count} 条订单，本次next_page_token: {new_next_page_token}")
        print("本次返回orders数量：", len(orders))
        print("本次返回next_page_token：", new_next_page_token)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(order_dict.values()), f, ensure_ascii=False, indent=2)

        if not new_next_page_token or not orders or synced_count >= total_count:
            break

        next_page_token = new_next_page_token
        time.sleep(0.5)

    print(f"同步完成，共保存 {synced_count} 条订单到 {OUTPUT_FILE}")


def fetch_and_save_orders():
    # 这里假设你已经拿到response对象
    response = requests.get(INPUT_URL)  # 实际用你的请求方式
    data = response.json()
    # 官方返回结构：{"code":0, "data": {"orders": [...]}, ...}
    orders = []
    if data.get("code") == 0 and data.get("data") and "orders" in data["data"]:
        orders = data["data"]["orders"]
    else:
        print("返回数据结构异常或无orders字段！")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(orders)} 条订单到 {OUTPUT_FILE}")


if __name__ == "__main__":
    sync_orders()
    # fetch_and_save_orders()  # 已不再需要外部API直连 