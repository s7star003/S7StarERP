from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import json
from pathlib import Path
import time

def load_config():
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'ToktokConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

def get_token_file():
    return Path(__file__).parent.parent.parent / 'Datas' / 'TiktokDatas' / 'token_storage_tiktok.json'

def load_token():
    token_file = get_token_file()
    if not token_file.exists():
        return None
    with open(token_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_token(token_data):
    token_file = get_token_file()
    print(f"[DEBUG] 即将保存到 {token_file}，内容为：{token_data}")
    with open(token_file, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)
    print(f"[DEBUG] token 已保存到 {token_file}")

def refresh_token_main():
    config = load_config()
    token_data = load_token()
    if not token_data or 'refresh_token' not in token_data:
        print('[ERROR] token_storage_tiktok.json 缺少 refresh_token')
        return
    refresh_token = token_data['refresh_token']
    url = (
        "https://auth.tiktok-shops.com/api/v2/token/refresh?"
        f"app_key={config['AppKey']}"
        f"&app_secret={config['AppSecret']}"
        f"&refresh_token={refresh_token}"
        f"&grant_type=refresh_token"
    )
    try:
        resp = requests.get(url)
        data = resp.json()
        if "data" in data:
            token_data = data["data"]
            token_data["obtained_at"] = int(time.time())
            print("[DEBUG] refresh_token_main 获取到新 token_data:", token_data)
            save_token(token_data)
            print("[INFO] 自动刷新 TikTok token 成功")
        else:
            print("[ERROR] 自动刷新 TikTok token 失败：", data)
    except Exception as e:
        print("[ERROR] 自动刷新 TikTok token 异常：", e)

@api_view(['GET'])
@swagger_auto_schema(
    operation_description="刷新TikTok access_token（refresh_token 从 token_storage_tiktok.json 获取）",
    responses={200: '返回新的access_token'}
)
def refresh_token_view(request):
    config = load_config()
    token_data = load_token()
    if not token_data or 'refresh_token' not in token_data:
        return JsonResponse({'error': 'token_storage_tiktok.json 缺少 refresh_token'}, status=400)
    refresh_token = token_data['refresh_token']
    url = (
        "https://auth.tiktok-shops.com/api/v2/token/refresh?"
        f"app_key={config['AppKey']}"
        f"&app_secret={config['AppSecret']}"
        f"&refresh_token={refresh_token}"
        f"&grant_type=refresh_token"
    )
    try:
        resp = requests.get(url)
        data = resp.json()
        if "data" in data:
            token_data = data["data"]
            token_data["obtained_at"] = int(time.time())
            print("[DEBUG] refresh_token_view 获取到新 token_data:", token_data)
            save_token(token_data)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

if __name__ == "__main__":
    refresh_token_main() 