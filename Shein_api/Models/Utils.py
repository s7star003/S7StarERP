import random
import string
from Crypto.Cipher import AES
import base64
from Crypto.Util.Padding import unpad

def get_random_key(length=5):
    """
    生成指定长度的随机数字+字母字符串，默认5位
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def shein_secretkey_decrypt_v3(ciphertext: str, key: str, iv_seed: str = "space-station-de") -> str:
    """
    SHEIN密钥解密，AES-128-CBC/PKCS7Padding，key为AppSecret前16位，iv为'space-station-de'
    """
    key_bytes = key[:16].encode("utf-8")
    iv = iv_seed.encode("utf-8")[:16]
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    raw = base64.b64decode(ciphertext)
    decrypted = cipher.decrypt(raw)
    return unpad(decrypted, AES.block_size).decode("utf-8")