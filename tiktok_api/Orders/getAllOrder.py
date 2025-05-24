import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../Datas/tiktok_orders.json")

def get_all_orders():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
    except Exception as e:
        print(f"读取{OUTPUT_FILE}失败: {e}")
        return []
    return orders

@csrf_exempt
def get_all_orders_view(request):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
    except Exception as e:
        return JsonResponse({"error": f"读取{OUTPUT_FILE}失败: {e}"}, status=500)
    return JsonResponse({"orders": orders, "count": len(orders)})

if __name__ == "__main__":
    orders = get_all_orders()
    print(f"共获取到 {len(orders)} 条订单")
    # 如需查看部分内容，可取消下行注释
    # print(json.dumps(orders[:3], ensure_ascii=False, indent=2)) 