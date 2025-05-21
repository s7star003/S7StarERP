import time
import json
import hashlib
import hmac
import base64
import requests
from urllib.parse import urlencode, quote

def get_current_timestamp():
    return int(time.time())

def generate_nonce():
    return str(int(time.time() * 1000))

def build_query_string(params):
    # TikTok Shop 要求参数按字典序排序
    return urlencode(sorted(params.items()), quote_via=quote)

def generate_sign(method, api_path, params, body, app_secret):
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

def get_order_list(page_size, body_content=None):
    # 读取配置和token
    with open('../config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)["TikTok"]
    with open('token_storage.json', 'r', encoding='utf-8') as f:
        token_data = json.load(f)

    app_key = config["AppKey"]
    app_secret = config["AppSecret"]
    shop_cipher = config["shopId"]  # 如果你有 shop_cipher 字段请替换
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

    request_body_json = body_content if body_content else "{}"
    sign = generate_sign("POST", api_path, parameters, request_body_json, app_secret)
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

if __name__ == "__main__":
    # 示例调用
    get_order_list(10)