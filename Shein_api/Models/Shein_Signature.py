from Crypto.Cipher import AES
import base64
import hmac
import hashlib


def generate_shein_signature(open_key_id, secret_key, path, timestamp, random_key):
    """
    生成SHEIN API签名
    """
    # 步骤一：组装签名数据VALUE
    value = f"{open_key_id}&{timestamp}&{path}"
    # print(f"步骤一 - 签名数据VALUE: {value}")
    # 步骤二：组装签名密钥KEY
    key = f"{secret_key}{random_key}"
    # print(f"步骤二 - 签名密钥KEY: {key}")
    # 步骤三：HMAC-SHA256计算并转换为十六进制
    hmac_result = hmac.new(key.encode('utf-8'), value.encode('utf-8'), hashlib.sha256).digest()
    hex_signature = hmac_result.hex()
    # print(f"步骤三 - HMAC-SHA256结果(HEX): {hex_signature}")
    # 步骤四：Base64编码
    base64_signature = base64.b64encode(hex_signature.encode('utf-8')).decode('utf-8')
    # print(f"步骤四 - Base64编码结果: {base64_signature}")
    # 步骤五：拼接RandomKey
    final_signature = f"{random_key}{base64_signature}"
    # print(f"步骤五 - 最终签名: {final_signature}")
    return final_signature 