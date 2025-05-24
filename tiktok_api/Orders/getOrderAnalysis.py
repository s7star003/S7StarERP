import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../Datas/OrderAnalysis.json")

@csrf_exempt
def get_order_analysis_view(request):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            analysis = json.load(f)
    except Exception as e:
        return JsonResponse({"error": f"读取{OUTPUT_FILE}失败: {e}"}, status=500)
    return JsonResponse({"analysis": analysis, "count": len(analysis)}) 