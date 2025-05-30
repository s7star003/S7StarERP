import requests
import json
import time
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from Shein_api.Models.Shein_Signature import generate_shein_signature
import random
import string

SAVE_PATH = Path(__file__).parent.parent.parent / 'Datas' / 'SheinDatas' / 'Shein_SecretKey.json'
CONFIG_PATH = Path(__file__).parent.parent.parent / 'Config' / 'SheinConfig' / 'config.json'

@swagger_auto_schema(
    method="get",
    operation_summary="SHEIN授权回调",
    operation_description="SHEIN授权回调接口，收到tempToken后自动请求openapi换密钥并写入本地JSON。",
    manual_parameters=[],
    responses={200: '返回token信息及回调参数'}
)
@api_view(["GET"])
def shein_callback(request):
    params = request.query_params.dict()
    tempToken = params.get("tempToken")
    appid = params.get("appid")
    # 从 config.json 读取 appsecret
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if "Shein" in config:
            appsecret = config["Shein"].get("AppSecret", "")
    shein_secret_info = None
    error = None
    if tempToken and appid and appsecret:
        url = "https://openapi.sheincorp.com/open-api/auth/get-by-token"
        payload = {"tempToken": tempToken}
        timestamp = str(int(time.time() * 1000))
        # 生成16位随机字符串作为random_key
        random_key = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        path = "/open-api/auth/get-by-token"
        print(f"[DEBUG] appid: {appid}")
        print(f"[DEBUG] appsecret: {appsecret}")
        print(f"[DEBUG] path: {path}")
        print(f"[DEBUG] timestamp: {timestamp}")
        print(f"[DEBUG] random_key: {random_key}")
        signature = generate_shein_signature(appid, appsecret, path, timestamp, random_key)
        headers = {
            "x-lt-appid": appid,
            "x-lt-timestamp": timestamp,
            "x-lt-signature": signature,
            "Content-Type": "application/json;charset=UTF-8"
        }
        print(f"[DEBUG] 请求URL: {url}")
        for k, v in headers.items():
            print(f"{k}: {v}")
        print(f"[DEBUG] 请求体: {json.dumps(payload, ensure_ascii=False)}")
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            # 尝试解析为 JSON，包装美观输出
            try:
                data = resp.json()
                # 抓取 info 字段并写入 token_storage.json
                info = data.get('info')
                if info:
                    token_path = Path(__file__).parent.parent.parent / 'Datas' / 'SheinDatas' / 'token_storage.json'
                    token_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(token_path, 'w', encoding='utf-8') as f:
                        json.dump(info, f, ensure_ascii=False, indent=2)
                return Response({
                    "code": data.get("code", resp.status_code),
                    "msg": data.get("msg", ""),
                    "data": data,
                    "debug": {
                        "appid": appid,
                        "timestamp": timestamp,
                        "random_key": random_key,
                        "signature": signature
                    }
                }, status=resp.status_code)
            except Exception:
                # 不是 JSON，原样输出
                return Response({
                    "code": resp.status_code,
                    "msg": "非JSON响应",
                    "data": resp.text
                }, status=resp.status_code)
        except Exception as e:
            error = str(e)
            return Response({'error': error}, status=500)
    else:
        error = "缺少tempToken、appid或appSecret参数"
        return Response({'error': error}, status=400)