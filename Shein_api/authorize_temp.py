from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponseRedirect
import base64
import time
from pathlib import Path
import json

@api_view(["GET"])
def authorizate_temp(request):
    config_path = Path(__file__).parent.parent / 'Datas' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)["Shein"]
    auth_url = "https://openapi-sem.sheincorp.com/#/empower"
    redirect_url = config.get("RedirectUri", "")
    appid = config.get("AppKey", "")
    state = f"AUTH-SHEIN-{int(time.time() * 1000)}"
    redirect_url_b64 = base64.b64encode(redirect_url.encode("utf-8")).decode("utf-8")
    url = f"{auth_url}?appid={appid}&redirectUrl={redirect_url_b64}&state={state}"
    return HttpResponseRedirect(url)