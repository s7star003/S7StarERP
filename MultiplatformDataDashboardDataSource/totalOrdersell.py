import json
from pathlib import Path

# 读取订单状态映射
tiktok_orders_path = Path(__file__).parent.parent / 'Datas' / 'TiktokDatas' / 'tiktok_orders.json'
with open(tiktok_orders_path, 'r', encoding='utf-8') as f:
    orders = json.load(f)
order_status_map = {str(order.get('id')): order.get('status') for order in orders}

# 统计tiktok_orders.json
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

# 统计OrdersPriceDetail.json中所有订单的总价格（通过order_id关联退单状态）
price_detail_path = Path(__file__).parent.parent / 'Datas' / 'TiktokDatas' / 'OrdersPriceDetail.json'
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
        if order_id == "576725259837476749":
            print(f"调试：明细order_id={order_id}，对应订单状态={status}")
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