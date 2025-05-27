from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
import requests
import json
import os

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_amazon_token(request):
    """
    刷新亚马逊 access_token。
    """
    # 读取本地 refresh_token
    token_path = 'Datas/AmazonDatas/token_storage_amazon.json'
    if not os.path.exists(token_path):
        return Response({'error': 'token 文件不存在'}, status=400)
    with open(token_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    refresh_token = token_data.get('refresh_token')
    if not refresh_token:
        return Response({'error': '未找到 refresh_token'}, status=400)
    client_id = getattr(settings, 'AMAZON_CLIENT_ID', 'your_amazon_client_id')
    client_secret = getattr(settings, 'AMAZON_CLIENT_SECRET', 'your_amazon_client_secret')
    token_url = 'https://api.amazon.com/auth/o2/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(token_url, data=data, headers=headers)
    try:
        new_token_data = resp.json()
    except Exception:
        new_token_data = {'error': '解析token响应失败', 'raw': resp.text}
    # 保存新token
    try:
        with open(token_path, 'w', encoding='utf-8') as f:
            json.dump(new_token_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        new_token_data['file_save_error'] = str(e)
    return Response(new_token_data) 