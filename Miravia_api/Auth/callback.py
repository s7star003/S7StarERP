import uuid
import json
import time
import requests
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse
from Miravia_api.Models.Utils import generate_uuid
from Miravia_api.Models.Miravia_Signature import generate_sign
import hmac
import hashlib

CONFIG_PATH = Path(__file__).parent.parent.parent / 'Config' / 'MiraviaConfig' / 'config.json'
TOKEN_PATH = Path(__file__).parent.parent.parent / 'Datas' / 'MiraviaDatas' / 'token_storage.json'
API_PATH = "/rest/auth/token/create"
SIGN_PATH = "/auth/token/create"
BASE_URL = "https://api.miravia.es"

@swagger_auto_schema(
    method="post",
    operation_summary="Miravia授权回调",
    operation_description="POST/GET参数由请求动态获取，签名规则严格按官方。",
    manual_parameters=[],
    responses={200: '返回token信息body'}
)
@api_view(["GET", "POST"])
def miravia_callback(request):
    if request.method == "GET":
        code = request.GET.get("code", "")
        uuid_str = request.GET.get("uuid", None)
        if code:
            # 自动用code发起签名并POST到Miravia
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                if "Miravia" in config:
                    app_key = config["Miravia"].get("AppKey", "")
                    app_secret = config["Miravia"].get("AppSecret", "")
                    print("app_secret repr:", repr(app_secret))
            else:
                return Response({'error': '缺少Miravia配置文件'}, status=500)
            if not uuid_str:
                uuid_str = generate_uuid()
            if code and uuid_str and app_key and app_secret:
                uuid_11 = str(uuid.uuid4()).replace('-', '')[:11]
                timestamp = str(int(time.time() * 1000))
                params = {
                    'code': code,
                    'uuid': uuid_11,
                    'app_key': app_key,
                    'sign_method': 'sha256',
                    'timestamp': timestamp,
                }
                sign = generate_sign(SIGN_PATH, params, app_secret)
                params['sign'] = sign
                print(f"[sign_method] sha256 [uuid] {uuid_11}")
                print(f"[签名原始串]", SIGN_PATH + ''.join(f'{k}{params[k]}' for k in sorted(params) if k != 'sign'))
                print(f"[sign] {sign}")
                print("[Miravia实际请求参数]", params)
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                try:
                    resp = requests.post(BASE_URL + API_PATH, data=params, headers=headers, timeout=10)
                    print("[Miravia原始返回]", resp.status_code, resp.text)
                    html = f"<h4>Miravia原始返回:</h4><pre>{resp.text}</pre>"
                    return HttpResponse(html, content_type="text/html; charset=utf-8", status=resp.status_code)
                except Exception as e:
                    html = f"<h3>请求异常:</h3><pre>{str(e)}</pre>"
                    return HttpResponse(html, content_type="text/html; charset=utf-8", status=500)
            else:
                return Response({'error': '缺少code、uuid、app_key或app_secret参数'}, status=400)
        # 无code时展示表单
        html = """
        <h3>Miravia 授权回调</h3>
        <form method='post'>
            code: <input name='code' style='width:400px'>
            <button type='submit'>提交</button>
        </form>
        <p>请在上方输入code，点击提交后将自动POST到Miravia接口并返回原始响应。</p>
        """
        return HttpResponse(html, content_type="text/html; charset=utf-8")
    # POST请求逻辑保持不变
    if request.method == "POST":
        code = request.data.get("code") or request.POST.get("code", "")
        uuid_str = request.data.get("uuid") or request.POST.get("uuid", None)
        if not code:
            return Response({"error": "请在URL或body中传递code参数"}, status=400)
        if not uuid_str:
            uuid_str = generate_uuid()
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if "Miravia" in config:
                app_key = config["Miravia"].get("AppKey", "")
                app_secret = config["Miravia"].get("AppSecret", "")
                print("app_secret repr:", repr(app_secret))
        else:
            return Response({'error': '缺少Miravia配置文件'}, status=500)
        if code and uuid_str and app_key and app_secret:
            uuid_11 = str(uuid.uuid4()).replace('-', '')[:11]
            timestamp = str(int(time.time() * 1000))
            params = {
                'code': code,
                'uuid': uuid_11,
                'app_key': app_key,
                'sign_method': 'sha256',
                'timestamp': timestamp,
            }
            sign = generate_sign(SIGN_PATH, params, app_secret)
            params['sign'] = sign
            print(f"[sign_method] sha256 [uuid] {uuid_11}")
            print(f"[签名原始串]", SIGN_PATH + ''.join(f'{k}{params[k]}' for k in sorted(params) if k != 'sign'))
            print(f"[sign] {sign}")
            print("[Miravia实际请求参数]", params)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            try:
                resp = requests.post(BASE_URL + API_PATH, data=params, headers=headers, timeout=10)
                print("[Miravia原始返回]", resp.status_code, resp.text)
                html = f"<h4>Miravia原始返回:</h4><pre>{resp.text}</pre>"
                return HttpResponse(html, content_type="text/html; charset=utf-8", status=resp.status_code)
            except Exception as e:
                html = f"<h3>请求异常:</h3><pre>{str(e)}</pre>"
                return HttpResponse(html, content_type="text/html; charset=utf-8", status=500)
        else:
            return Response({'error': '缺少code、uuid、app_key或app_secret参数'}, status=400)
