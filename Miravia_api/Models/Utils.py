import uuid

def generate_uuid():
    """
    生成11位数字uuid字符串（Miravia授权专用，和官网示例一致）。
    """
    return str(uuid.uuid4().int)[:11]
