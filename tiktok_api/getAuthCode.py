import json
import webbrowser
import subprocess
import sys
import time
from pathlib import Path
import os
from django.http import JsonResponse
from .getAccessToken import get_access_token

def load_config():
    config_path = Path(__file__).parent.parent / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

def build_auth_url(app_key, redirect_uri,region="ES"):
    base_url = "https://auth.tiktok-shops.com/oauth/authorize"
    params = (
        f"app_key={app_key}&"
        f"redirect_uri={redirect_uri}&"
        f"state=xyz"
        f"response_type=code&"
        f"region={region}&"
    )
    return f"{base_url}?{params}"

def tiktok_callback(request):
    try:
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)
        token_info = get_access_token(code)
        if not token_info:
            return JsonResponse({'error': '获取AccessToken失败'}, status=500)
        return JsonResponse(token_info)
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 终端输出详细错误
        return JsonResponse({'error': str(e)}, status=500)

if __name__ == "__main__":
    config = load_config()
    auth_url = build_auth_url(config["AppKey"], config["RedirectUri"])
    print("打开浏览器进行TikTok授权...")
    webbrowser.open(auth_url)

    # 启动Django服务 (假设 manage.py 在当前目录)
    print("启动Django服务监听回调...")

    # Windows用户可能需要管理员权限监听80端口，或者改成其他端口
    # 推荐用端口80以外的端口，比如8080，注意同时修改 RedirectUri 配置和代码
    port = 80

    # 运行django runserver命令
    project_root = Path(__file__).parent.parent
    manage_py = project_root / "manage.py"
    proc = subprocess.Popen(["python", str(manage_py), "runserver", "0.0.0.0:8000"])

    print("Django服务器已启动，等待授权回调...")
