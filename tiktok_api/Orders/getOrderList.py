import time
import json
import hashlib
import hmac
import base64
import requests
from Tiktok_api.Models.Utils import get_current_timestamp, generate_nonce, build_query_string
from Tiktok_api.Models.sign_utils import generate_sign
from django.conf import settings
from pathlib import Path
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import urlencode, quote

def get_current_timestamp():
    return int(time.time())

def generate_nonce():
    return str(int(time.time() * 1000))

def build_query_string(params):
    # TikTok Shop 要求参数按字典序排序
    return urlencode(sorted(params.items()), quote_via=quote)
    # 1. method大写
    method = method.upper()
    # 2. path
    # 3. query string（已排序）
    query = build_query_string(params)
    # 4. body（字符串，不能有空格）
    body_str = body if body else ""
    # 5. 拼接
    sign_str = f"{method}{api_path}{query}{body_str}"
    # 6. HMAC-SHA256
    sign = hmac.new(app_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).digest()
    # 7. base64
    return base64.b64encode(sign).decode('utf-8')

def get_order_list(page_size, next_page_token=None, body_content=None):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(PROJECT_ROOT, "Config", "ToktokConfig", "config.json")
    token_path = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "token_storage_tiktok.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)["TikTok"]
    with open(token_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)

    app_key = config["AppKey"]
    app_secret = config["AppSecret"]
    shop_cipher = config.get("shopCipher", "")  # 密文ID
    shop_id = config.get("shopId", "")          # 明文ID
    access_token = token_data["access_token"]

    timestamp = str(get_current_timestamp())
    nonce = generate_nonce()

    api_path = "/order/202309/orders/search"
    parameters = {
        "access_token": access_token,
        "app_key": app_key,
        "nonce": nonce,
        "shop_cipher": shop_cipher,
        "timestamp": timestamp,
        "page_size": str(page_size)
    }
    if next_page_token:
        parameters["page_token"] = next_page_token  # 只作为URL参数传递
    # 构建请求体
    if body_content:
        body = json.loads(body_content)
    else:
        body = {}
    # 不再放page_token到body里
    request_body_json = json.dumps(body, ensure_ascii=False)
    # 生成签名时，parameters 不含 sign
    sign = generate_sign(api_path, parameters, request_body_json, app_secret)
    parameters["sign"] = sign
    query_string = build_query_string(parameters)
    url = f"https://open-api.tiktokglobalshop.com{api_path}?{query_string}"
    headers = {
        "Content-Type": "application/json",
        "x-tts-access-token": access_token
    }
    print("请求URL:", url)
    print("请求体:", request_body_json)
    response = requests.post(url, data=request_body_json, headers=headers)
    print("响应状态码:", response.status_code)
    print("响应内容:", response.text)
    return response.text

page_size_param = openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER, default=10)
next_page_token_param = openapi.Parameter('next_page_token', openapi.IN_QUERY, description="翻页token", type=openapi.TYPE_STRING, required=False)
body_content_param = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "start_time": openapi.Schema(type=openapi.TYPE_INTEGER, description="开始时间"),
        "end_time": openapi.Schema(type=openapi.TYPE_INTEGER, description="结束时间"),
        "order_status": openapi.Schema(type=openapi.TYPE_INTEGER, description="订单状态"),
        "page_size": openapi.Schema(type=openapi.TYPE_INTEGER, description="每页数量"),
        "sort_by": openapi.Schema(type=openapi.TYPE_STRING, description="排序字段"),
        "cursor": openapi.Schema(type=openapi.TYPE_STRING, description="翻页游标"),
        # ... 其他字段 ...
    },
    description="body_content参数，JSON对象，内容会作为请求体传递到TikTok API"
)

@swagger_auto_schema(
    method='post',
    operation_description="获取订单列表",
    manual_parameters=[page_size_param, next_page_token_param],
    request_body=body_content_param,
    responses={200: openapi.Response('返回订单列表')}
)
@api_view(['POST'])
def get_order_list_view(request):
    page_size = int(request.GET.get('page_size', 10))
    next_page_token = request.GET.get('next_page_token')
    body_content = None
    if request.body:
        try:
            body_content = request.body.decode('utf-8')
        except Exception:
            body_content = None
    result = get_order_list(page_size, next_page_token, body_content)
    try:
        return Response(json.loads(result))
    except Exception:
        return Response(result)

@swagger_auto_schema(
    method='get',
    operation_description="GET方式获取订单列表，body_content为JSON字符串，作为请求体传递到TikTok API",
    manual_parameters=[
        openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER, default=10),
        openapi.Parameter('body_content', openapi.IN_QUERY, description="body_content参数，JSON字符串", type=openapi.TYPE_STRING, required=False)
    ],
    responses={200: openapi.Response('返回订单列表')}
)
@api_view(['GET'])
def get_order_list_view_get(request):
    page_size = int(request.GET.get('page_size', 10))
    body_content = request.GET.get('body_content')
    result = get_order_list(page_size, body_content=body_content)
    try:
        return Response(json.loads(result))
    except Exception:
        return Response(result)

if __name__ == "__main__":
    # 示例调用
    get_order_list(10)