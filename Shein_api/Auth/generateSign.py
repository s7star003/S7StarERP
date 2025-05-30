import hmac
import hashlib
import base64
import random
import string
import json
import os
import time
import sys

def generate_random_key(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_shein_signature(open_key_id, secret_key, path, timestamp, random_key):
    # 步骤一：组装签名数据VALUE
    value = f"{open_key_id}&{timestamp}&{path}"
    print(f"步骤一 - 签名数据VALUE: {value}")
    
    # 步骤二：组装签名密钥KEY
    key = f"{secret_key}{random_key}"
    print(f"步骤二 - 签名密钥KEY: {key}")
    
    # 步骤三：HMAC-SHA256计算并转换为十六进制
    hmac_result = hmac.new(key.encode('utf-8'), value.encode('utf-8'), hashlib.sha256).digest()
    hex_signature = hmac_result.hex()
    print(f"步骤三 - HMAC-SHA256结果(HEX): {hex_signature}")
    
    # 步骤四：Base64编码
    base64_signature = base64.b64encode(hex_signature.encode('utf-8')).decode('utf-8')
    print(f"步骤四 - Base64编码结果: {base64_signature}")
    
    # 步骤五：拼接RandomKey
    final_signature = f"{random_key}{base64_signature}"
    print(f"步骤五 - 最终签名: {final_signature}")
    
    return final_signature

# 示例调用
if __name__ == "__main__":
    # 从token_storage_shein.json读取open_key_id和secret_key
    token_path = os.path.join(os.path.dirname(__file__), "..", "Datas", "token_storage_shein.json")
    with open(token_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    open_key_id = token_data.get("openKeyId", "")
    secret_key = token_data.get("secretKey", "")
    if len(sys.argv) < 2:
        print("用法: python generateSign.py <PATH>")
        sys.exit(1)
    path = sys.argv[1]
    timestamp = str(int(time.time() * 1000))  # 当前时间戳（毫秒）
    random_key = generate_random_key()  # 自动生成5位随机字符串

    signature = generate_shein_signature(open_key_id, secret_key, path, timestamp, random_key)
    print("最终签名：", signature)