import json
import time
import requests
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / 'config.json'
# Token 存储路径
TOKEN_FILE = Path(__file__).parent / 'token_storage.json'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_token(token_data):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)

def get_access_token(auth_code):
    config = load_config()
    tiktok_conf = config.get("TikTok", {})

    url = (
        "https://auth.tiktok-shops.com/api/v2/token/get?"
        f"app_key={tiktok_conf.get('AppKey')}&"
        f"app_secret={tiktok_conf.get('AppSecret')}&"
        f"auth_code={auth_code}&"
        f"grant_type=authorized_code&"
        f"redirect_uri={tiktok_conf.get('RedirectUri')}"
    )

    print("请求URL:", url)
    response = requests.get(url)
    print("响应状态码:", response.status_code)
    print("响应内容:", response.text)

    if response.status_code != 200:
        print("请求失败:", response.status_code, response.text)
        return None

    data = response.json()
    if "data" not in data:
        print("响应格式异常:", data)
        return None

    token_data = data["data"]
    token_data["obtained_at"] = int(time.time())

    save_token(token_data)
    print("Access Token 已保存到", TOKEN_FILE)
    return token_data

if __name__ == "__main__":
    import sys
    print("【回调已调用 getAccessToken.py】")  # 明确输出
    if len(sys.argv) != 2:
        print("用法: python getAccessToken.py <auth_code>")
        sys.exit(1)

    auth_code = sys.argv[1]
    token_info = get_access_token(auth_code)
    if token_info:
        print("获取到的 Access Token:", token_info.get("access_token"))
