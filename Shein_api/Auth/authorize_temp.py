from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponseRedirect
import base64
import time
from pathlib import Path
import json
from drf_yasg.utils import swagger_auto_schema
import os

@swagger_auto_schema(
    method="get",
    operation_summary="SHEIN授权跳转",
    operation_description="跳转到SHEIN授权页面，获取临时token。",
    responses={302: '重定向到SHEIN授权页面'}
)
@api_view(["GET"])
def authorizate_temp(request):
    config_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'Config' / 'SheinConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)["Shein"]
    auth_url = "https://openapi-sem.sheincorp.com/#/empower"
    redirect_url = config.get("RedirectUri", "")
    appid = config.get("AppKey", "")
    state = f"AUTH-SHEIN-{int(time.time() * 1000)}"
    redirect_url_b64 = base64.b64encode(redirect_url.encode("utf-8")).decode("utf-8")
    url = f"{auth_url}?appid={appid}&redirectUrl={redirect_url_b64}&state={state}"
    return HttpResponseRedirect(url)