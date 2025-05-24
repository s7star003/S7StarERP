import json
import time
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from django.conf import settings
from .getOrderList import get_order_list
from .getOrderDetail import get_order_detail
from .getPriceDetail import get_price_detail
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response

def get_order_list_view(request):
    page_size = int(request.GET.get("page_size", 10))
    # 你可以根据需要支持更多参数
    try:
        result = get_order_list(page_size)
        return JsonResponse(json.loads(result), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@swagger_auto_schema(
    method='get',
    operation_description="获取TikTok订单详情",
    manual_parameters=[
        openapi.Parameter('order_ids', openapi.IN_QUERY, description="订单ID，多个用逗号分隔", type=openapi.TYPE_STRING, required=True)
    ],
    responses={200: openapi.Response('订单详情', schema=openapi.Schema(type=openapi.TYPE_OBJECT))}
)
@api_view(['GET'])
def get_order_detail_view(request):
    order_ids = request.GET.get("order_ids", "")
    if not order_ids:
        return JsonResponse({"error": "缺少 order_ids 参数"}, status=400)
    try:
        result = get_order_detail(order_ids)
        return JsonResponse(json.loads(result), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# --- 新增价格明细接口 ---
@swagger_auto_schema(
    method='get',
    operation_description="获取TikTok订单价格明细",
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_QUERY, description="订单ID", type=openapi.TYPE_STRING, required=True)
    ],
    responses={200: openapi.Response('价格明细', schema=openapi.Schema(type=openapi.TYPE_OBJECT))}
)
@api_view(['GET'])
def get_price_detail_view(request):
    order_id = request.GET.get("order_id", "")
    if not order_id:
        return Response({"error": "缺少 order_id 参数"}, status=400)
    try:
        result = get_price_detail(order_id)
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
