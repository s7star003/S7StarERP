import json
import time
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from django.conf import settings
from .get_order_list import get_order_list
from .get_order_detail import get_order_detail

# 令牌存储路径
TOKEN_FILE = Path(settings.BASE_DIR) / 'token_storage.json'

# 读取配置
def load_config():
    config_path = Path(settings.BASE_DIR) / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

# 保存token到文件
def save_token(token_data):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)

@csrf_exempt
def tiktok_callback(request):
    auth_code = request.GET.get('auth_code') or request.GET.get('code')
    if not auth_code:
        return HttpResponse("未获取到授权码", status=400)

    config = load_config()

    # 换取AccessToken
    url = "https://open.tiktokapis.com/oauth/access_token/"
    payload = {
        "client_key": config["AppKey"],
        "client_secret": config["AppSecret"],
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": config["RedirectUri"],
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        return HttpResponse(f"获取AccessToken失败: {resp.text}", status=500)

    data = resp.json()
    if "data" not in data:
        return HttpResponse(f"响应格式异常: {data}", status=500)

    token_data = data["data"]
    token_data["obtained_at"] = int(time.time())
    save_token(token_data)

    return HttpResponse("<h2>授权成功，AccessToken已保存，可以关闭此页面。</h2>")

def get_order_list_view(request):
    page_size = int(request.GET.get("page_size", 10))
    # 你可以根据需要支持更多参数
    try:
        result = get_order_list(page_size)
        return JsonResponse(json.loads(result), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_order_detail_view(request):
    order_ids = request.GET.get("order_ids", "")
    if not order_ids:
        return JsonResponse({"error": "缺少 order_ids 参数"}, status=400)
    try:
        result = get_order_detail(order_ids)
        return JsonResponse(json.loads(result), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
