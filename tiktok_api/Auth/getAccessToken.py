import json
import time
import requests
from pathlib import Path
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# 配置文件路径
try:
    BASE_DIR = settings.BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = Path(BASE_DIR) / 'Config' / 'ToktokConfig' / 'config.json'
# Token 存储路径
TOKEN_FILE = Path(BASE_DIR) / 'token_storage_tiktok.json'

def load_tiktok_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

def save_token(token_data):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)

def get_tiktok_access_token(auth_code):
    config = load_tiktok_config()
    url = (
        "https://auth.tiktok-shops.com/api/v2/token/get?"
        f"app_key={config['AppKey']}"
        f"&app_secret={config['AppSecret']}"
        f"&auth_code={auth_code}"
        f"&grant_type=authorized_code"
        f"&redirect_uri={config['RedirectUri']}"
    )
    print("请求URL:", url)
    response = requests.get(url)
    print("响应状态码:", response.status_code)
    print("响应内容:", response.text)
    if response.status_code != 200:
        print("请求失败:", response.status_code, response.text)
        return None, response.text
    data = response.json()
    if "data" not in data:
        print("响应格式异常:", data)
        return None, data
    token_data = data["data"]
    token_data["obtained_at"] = int(time.time())
    save_token(token_data)
    print("Access Token 已保存到", TOKEN_FILE)
    return token_data, None

# Django 视图：TikTok 回调
@csrf_exempt
def tiktok_callback(request):
    try:
        auth_code = request.GET.get('auth_code') or request.GET.get('code')
        print(f"收到回调，auth_code参数值: {auth_code}")
        if not auth_code:
            return HttpResponse("未获取到授权码", status=400)
        print("准备调用 get_tiktok_access_token")
        token_data, err = get_tiktok_access_token(auth_code)
        print(f"get_tiktok_access_token 返回: token_data={token_data}, err={err}")
        if not token_data:
            return HttpResponse(f"获取AccessToken失败: {err}", status=500)
        return HttpResponse("<h2>授权成功，AccessToken已保存，可以关闭此页面。</h2>")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        return HttpResponse(f"<pre>{tb}</pre>", status=500)

if __name__ == "__main__":
    import sys
    print("【回调已调用 getAccessToken.py】")
    if len(sys.argv) != 2:
        print("用法: python getAccessToken.py <auth_code>")
        sys.exit(1)
    auth_code = sys.argv[1]
    token_info, err = get_tiktok_access_token(auth_code)
    if token_info:
        print("获取到的 Access Token:", token_info.get("access_token"))
    else:
        print("获取失败:", err)
