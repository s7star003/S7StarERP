# 辅助函数可以写这里

import time
from urllib.parse import urlencode, quote

def get_current_timestamp():
    return int(time.time())

def generate_nonce():
    return str(int(time.time() * 1000))

def build_query_string(params):
    # 参数按字典序排序
    return urlencode(sorted(params.items()), quote_via=quote)
