import hashlib
import hmac

def generate_sign(path, parameters, request_body, app_secret):
    """
    生成 TikTok Shop Open Platform API 签名（与.NET算法一致）
    :param path: API路径，如 /order/202309/orders/search
    :param parameters: dict，参与签名的参数（不含 sign、access_token），已排序
    :param request_body: str，无空格JSON字符串
    :param app_secret: str
    :return: 小写hex字符串
    """
    sb = [path]
    for k, v in sorted(parameters.items()):
        if k.lower() in ("sign", "access_token"):
            continue
        sb.append(f"{k}{v}")
    if request_body:
        sb.append(request_body)
    sign_str = app_secret + ''.join(sb) + app_secret

    print(f"🔑 待签名字符串：{sign_str}")

    sign = hmac.new(app_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return sign