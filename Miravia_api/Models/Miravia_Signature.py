import hmac
import hashlib

def generate_sign(api_path, params, app_secret):
    """
    Miravia官方签名生成方法。
    :param api_path: str, 参与签名的API路径，如 /rest/auth/token/create
    :param params: dict, 所有请求参数（不含 sign）
    :param app_secret: str, 密钥
    :return: str, 大写16进制签名
    """
    if not isinstance(params, dict):
        raise TypeError(f"params 必须为 dict，实际为：{type(params)}，内容：{params}")
    sort_dict = sorted(params)
    parameters_str = "%s%s" % (
        api_path,
        ''.join('%s%s' % (key, params[key]) for key in sort_dict)
    )
    print("[签名原始串]", parameters_str)
    h = hmac.new(app_secret.encode("utf-8"), parameters_str.encode("utf-8"), digestmod=hashlib.sha256)
    return h.hexdigest().upper()
