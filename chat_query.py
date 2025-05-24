import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

ORDERS_FILE = os.path.join(os.path.dirname(__file__), "../Datas/tiktok_orders.json")
DEEPSEEK_API_KEY = "sk-6e450230bcfa4e16b60ae15a68d51817"  # 替换为你的Key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 替换为实际API地址

@csrf_exempt
def chat_query_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
        except Exception as e:
            return JsonResponse({"error": "请求格式错误"}, status=400)

        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except Exception as e:
            return JsonResponse({"error": "订单数据读取失败"}, status=500)

        # 只取部分数据防止超长
        orders_sample = orders[:30] if len(orders) > 30 else orders

        prompt = (
            "你是一个电商数据分析助手，用户会用中文提问，你需要根据订单数据回答问题。\n"
            "订单数据如下（JSON数组，每个元素为一个订单，包含商品信息、金额等字段）：\n"
            f"{json.dumps(orders_sample, ensure_ascii=False)}\n"
            f"用户问题：{question}\n"
            "请用简洁的中文直接给出分析结果。"
        )

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",  # 或 deepseek-coder 等
            "messages": [
                {"role": "system", "content": "你是一个专业的数据分析助手。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.2
        }

        try:
            resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return JsonResponse({"error": f"AI分析失败: {e}"}, status=500)

        return JsonResponse({"answer": answer})

    return JsonResponse({"error": "仅支持POST"}, status=405)
