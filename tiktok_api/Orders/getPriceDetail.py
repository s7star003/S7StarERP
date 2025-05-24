import os
import time
import requests
import json
from Tiktok_api.Models.sign_utils import generate_sign

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "Config", "ToktokConfig", "config.json")
TOKEN_PATH = os.path.join(PROJECT_ROOT, "Datas", "TiktokDatas", "token_storage_tiktok.json")


def load_tiktok_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

def load_tiktok_token():
    with open(TOKEN_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_price_detail(order_id):
    config = load_tiktok_config()
    token_data = load_tiktok_token()
    access_token = token_data["access_token"]
    app_key = config["AppKey"]
    app_secret = config["AppSecret"]
    shop_cipher = config.get("shopCipher")
    timestamp = str(int(time.time()))
    api_path = f"/order/202407/orders/{order_id}/price_detail"
    parameters = {
        "app_key": app_key,
        "timestamp": timestamp,
        "shop_cipher": shop_cipher
    }
    sign = generate_sign(api_path, parameters, None, app_secret)
    parameters["sign"] = sign
    query_string = "&".join(f"{k}={v}" for k, v in parameters.items())
    url = f"https://open-api.tiktokglobalshop.com{api_path}?{query_string}"
    headers = {
        "Content-Type": "application/json",
        "x-tts-access-token": access_token
    }
    print("请求URL:", url)
    resp = requests.get(url, headers=headers)
    try:
        return resp.json()
    except Exception:
        return {"error": "响应解析失败"}

if __name__ == "__main__":
    # 示例：传入订单ID
    order_id = input("请输入order_id: ")
    result = get_price_detail(order_id)
    print(json.dumps(result, ensure_ascii=False, indent=2)) 