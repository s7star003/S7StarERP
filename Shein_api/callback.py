from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json
from pathlib import Path

SHEIN_TOKEN_FILE = Path(__file__).parent.parent / 'Datas' / 'token_storage_shein.json'

# 获取openKeyId和secretKey并写入文件
def get_shein_token(temp_token):
    url = "https://openapi-sem.sheincorp.com/open-api/auth/get-by-token"
    payload = {"tempToken": temp_token}
    try:
        resp = requests.get(url, params=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # 假设返回结构为{"data": {"openKeyId": ..., "secretKey": ...}}
            if "data" in data and "openKeyId" in data["data"] and "secretKey" in data["data"]:
                with open(SHEIN_TOKEN_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data["data"], f, ensure_ascii=False, indent=2)
                return data["data"], None
            else:
                return None, f"返回格式异常: {data}"
        else:
            return None, f"请求失败: {resp.status_code} {resp.text}"
    except Exception as e:
        return None, str(e)

@api_view(["GET"])
def shein_callback(request):
    # 获取所有回调参数
    params = request.query_params.dict()
    tempToken = params.get("tempToken")
    appid = params.get("appid")
    token_info = None
    error = None
    if tempToken:
        token_info, error = get_shein_token(tempToken)
    return Response({
        "msg": "SHEIN授权回调成功！",
        "tempToken": tempToken,
        "appid": appid,
        "token_info": token_info,
        "error": error,
        "params": params
    })