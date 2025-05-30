import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import requests
import time
import datetime
from pathlib import Path
from collections import OrderedDict
from Shein_api.Models.Shein_Signature import generate_shein_signature
from Shein_api.Models.Utils import get_random_key, shein_secretkey_decrypt_v3

def batch_get_orders():
    # 读取token和密钥
    token_path = Path(__file__).parent.parent.parent / 'Datas' / 'SheinDatas' / 'token_storage.json'
    with open(token_path, 'r', encoding='utf-8') as f:
        token_info = json.load(f)
    secretKey = token_info.get('secretKey')
    openKeyId = token_info.get('openKeyId')
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'SheinConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    appSecret = config['Shein']['AppSecret']
    secretKeyDecrypt = shein_secretkey_decrypt_v3(secretKey, appSecret)
    # 初始化时间
    start_dt = datetime.datetime.strptime('2025-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    now_dt = datetime.datetime.now()
    all_orders = []
    orders_path = Path(__file__).parent.parent.parent / 'Datas' / 'SheinDatas' / 'shein_orders.json'
    if orders_path.exists():
        with open(orders_path, 'r', encoding='utf-8') as f:
            try:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    all_orders = loaded
                else:
                    all_orders = []
            except Exception:
                all_orders = []
    while start_dt < now_dt:
        end_dt = start_dt + datetime.timedelta(days=1)
        # 生成签名参数
        timestamp = str(int(time.time() * 1000))
        random_key = get_random_key(5)
        path = '/open-api/order/order-list'
        signature = generate_shein_signature(openKeyId, secretKeyDecrypt, path, timestamp, random_key)
        headers = {
            "Content-Type": "application/json",
            "x-lt-openKeyId": openKeyId,
            "x-lt-timestamp": timestamp,
            "x-lt-signature": signature
        }
        params = OrderedDict([
            ("queryType", "1"),
            ("startTime", start_dt.strftime('%Y-%m-%d %H:%M:%S')),
            ("endTime", end_dt.strftime('%Y-%m-%d %H:%M:%S')),
            ("page", "300"),
            ("pageSize", "30")
        ])
        base_url = "https://openapi.sheincorp.com/open-api/order/order-list"
        #print(f"[请求BODY]: {json.dumps(params, ensure_ascii=False)}")
        try:
            resp = requests.post(base_url, json=params, headers=headers, timeout=10)
            data = resp.json()
            #print(f"[返回JSON]: {json.dumps(data, ensure_ascii=False, indent=2)}")
            # 累加订单数据
            if 'info' in data and 'orderList' in data['info']:
                all_orders.extend(data['info']['orderList'])
            # 保存到本地
            with open(orders_path, 'w', encoding='utf-8') as f:
                json.dump(all_orders, f, ensure_ascii=False, indent=2)
            print(f"已拉取 {start_dt} ~ {end_dt}，本次订单数: {len(data.get('info', {}).get('orderList', []))}，累计: {len(all_orders)}")
        except Exception as e:
            print(f"请求异常: {e}")
        # 时间推进
        start_dt = end_dt
        # 速率限制
        time.sleep(1/90)

if __name__ == "__main__":
    batch_get_orders() 