import json
import requests
from urllib.parse import urlencode, quote
from django.conf import settings
from pathlib import Path
from .sign_utils import generate_sign
import time

def get_current_timestamp():
    return int(time.time())

def generate_nonce():
    return str(int(time.time() * 1000))

def build_query_string(params):
    # TikTok Shop 要求参数按字典序排序
    return urlencode(sorted(params.items()), quote_via=quote)

def get_order_detail(order_ids):
    config_path = Path(settings.BASE_DIR) / 'config.json'
    token_path = Path(settings.BASE_DIR) / 'tiktok_api' / 'token_storage.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)["TikTok"]
    with open(token_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)

    app_key = config["AppKey"]
    app_secret = config["AppSecret"]
    shop_cipher = config["shopCipher"]
    access_token = token_data["access_token"]

    timestamp = str(get_current_timestamp())
    nonce = generate_nonce()

    api_path = "/order/202309/orders"
    parameters = {
        "app_key": app_key,
        "ids": order_ids,  # 逗号分隔的订单ID字符串
        "shop_cipher": shop_cipher,
        "timestamp": timestamp
    }

    # GET请求没有请求体
    sign = generate_sign(api_path, parameters, None, app_secret)
    parameters["sign"] = sign

    query_string = build_query_string(parameters)
    url = f"https://open-api.tiktokglobalshop.com{api_path}?{query_string}"

    headers = {
        "x-tts-access-token": access_token
    }

    print("请求URL:", url)
    response = requests.get(url, headers=headers)
    print("响应状态码:", response.status_code)
    print("响应内容:", response.text)
    return response.text

if __name__ == "__main__":
    # 示例调用
    # get_order_detail("123456789012345,987654321098765")
    pass