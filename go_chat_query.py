import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

@require_GET
@csrf_exempt
def go_chat_query_view(request):
    question = request.GET.get('q', '请统计每个商品的销量')
    try:
        resp = requests.post('http://localhost:8000/api/TikTok/chatQuery', json={"question": question})
        return JsonResponse(resp.json(), safe=False)
    except Exception as e:
        return JsonResponse({"error": f"请求chatQuery失败: {e}"}, status=500)
