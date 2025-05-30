import json
import requests
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
import datetime
from Shein_api.Models.Shein_Signature import generate_shein_signature
from Shein_api.Models.Utils import get_random_key, shein_secretkey_decrypt_v3
from collections import OrderedDict

@swagger_auto_schema(
    method="post",
    operation_summary="获取SHEIN订单列表",
    operation_description="根据SHEIN官方API获取订单列表，自动读取本地token。",
    manual_parameters=[],
    responses={200: '订单列表'}
)
@api_view(["POST"])
def get_order_lists(request):
    """
    获取SHEIN订单列表，token自动读取本地token_storage.json。
    支持 query 参数透传。
    """
    # 读取本地token
    token_path = Path(__file__).parent.parent.parent / 'Datas' / 'SheinDatas' / 'token_storage.json'
    if not token_path.exists():
        return Response({"code": 401, "msg": "token未获取，请先授权。"}, status=status.HTTP_401_UNAUTHORIZED)
    with open(token_path, 'r', encoding='utf-8') as f:
        token_info = json.load(f)
    secretKey = token_info.get('secretKey')
    appid = token_info.get('appid')
    openKeyId = token_info.get('openKeyId')
    #print(f"[解密前secretKey]: {secretKey}")
    # 读取 AppSecret 作为解密 key
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'SheinConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    appSecret = config['Shein']['AppSecret']
    #print(f"[解密用AppSecret]: {appSecret}")
    secretKeyDecrypt = secretKey
    if secretKey:
        try:
            secretKeyDecrypt = shein_secretkey_decrypt_v3(secretKey, appSecret)
            print(f"[解密后secretKey]: {secretKeyDecrypt}")
        except Exception as e:
            print(f"[解密secretKey失败]: {e}")
            return Response({"code": 500, "msg": f"secretKey解密失败: {e}"}, status=500)
    # 打印原始 secretKey 和 openKeyId
    #print(f"[原始secretKey]: {token_info.get('secretKey')}")
    #print(f"[openKeyId]: {openKeyId}")
    #print(f"[secretKey长度]: {len(token_info.get('secretKey', ''))}")
    #print(f"[openKeyId长度]: {len(openKeyId or '')}")
    # 生成签名参数
    timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
    #timestamp = "1748450720798"
    random_key = get_random_key(5)
    #random_key = "w8NSn"
    path = '/open-api/order/order-list'
    #print(f"[签名参数] openKeyId: {openKeyId}")
    #print(f"[签名参数] secretKey: {secretKeyDecrypt}")
    #print(f"[签名参数] path: {path}")
    #print(f"[签名参数] timestamp: {timestamp}")
    #print(f"[签名参数] random_key: {random_key}")
    signature = generate_shein_signature(openKeyId, secretKeyDecrypt, path, timestamp, random_key)
    print(f"[签名结果] signature: {signature}")
    # 构造headers，严格对齐SHEIN官方接口要求
    headers = {
        "Content-Type": "application/json",
        "x-lt-openKeyId": openKeyId,
        "x-lt-timestamp": timestamp,
        "x-lt-signature": signature
    }

    print(f"[请求头]: {headers}")

    # 构造请求参数，全部硬编码
    now_dt = datetime.datetime.now()
    start_dt = now_dt - datetime.timedelta(days=1)
    params = OrderedDict([
        ("queryType", "1"),
        ("startTime", start_dt.strftime('%Y-%m-%d %H:%M:%S')),
        ("endTime", now_dt.strftime('%Y-%m-%d %H:%M:%S')),
        ("page", "300"),
        ("pageSize", "30")
    ])
    print(f"[请求BODY]: {json.dumps(params, ensure_ascii=False)}")
    base_url = "https://openapi.sheincorp.com/open-api/order/order-list"
    print(f"[请求URL]: {base_url}")
    try:
        resp = requests.post(base_url, json=params, headers=headers, timeout=10)
        data = resp.json()
        # 保存订单数据到本地 shein_orders.json
        orders_path = Path(__file__).parent.parent.parent / 'Datas' / 'SheinDatas' / 'shein_orders.json'
        orders_path.parent.mkdir(parents=True, exist_ok=True)
        with open(orders_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return Response({
            "code": data.get("code", resp.status_code),
            "msg": data.get("msg", ""),
            "data": data
        }, status=resp.status_code)
    except Exception as e:
        return Response({"code": 500, "msg": str(e)}, status=500) 