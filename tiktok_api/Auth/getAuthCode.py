import json
import webbrowser
import subprocess
import sys
import time
from pathlib import Path
import os
from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponseRedirect
import argparse

# 保留原有的 get_access_token 引用
from Tiktok_api.Auth.getAccessToken import get_tiktok_access_token

def load_config():
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'ToktokConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

def build_auth_url(app_key, redirect_uri, region="ES"):
    base_url = "https://auth.tiktok-shops.com/oauth/authorize"
    params = (
        f"app_key={app_key}&"
        f"redirect_uri={redirect_uri}&"
        f"state=xyz&"
        f"response_type=code&"
        f"region={region}"
    )
    return f"{base_url}?{params}"

# --- 新增：swagger 可见的授权地址生成接口 ---
@api_view(['GET'])
@swagger_auto_schema(
    operation_description="生成TikTok授权URL（点击返回的链接即可跳转）",
    manual_parameters=[
        openapi.Parameter('region', openapi.IN_QUERY, description="区域代码", type=openapi.TYPE_STRING, required=False, default='ES')
    ],
    responses={200: '返回授权URL'}
)
def get_tiktok_auth_url(request):
    config = load_config()
    region = request.GET.get('region', 'ES')
    auth_url = build_auth_url(config["AppKey"], config["RedirectUri"], region)
    return JsonResponse({'auth_url': auth_url})

# 保留原有 tiktok_callback 仅供参考（未注册路由）
def tiktok_callback(request):
    try:
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)
        token_info = get_tiktok_access_token(code)
        if not token_info:
            return JsonResponse({'error': '获取AccessToken失败'}, status=500)
        return JsonResponse(token_info)
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 终端输出详细错误
        return JsonResponse({'error': str(e)}, status=500)
