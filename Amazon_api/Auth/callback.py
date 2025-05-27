from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
import requests
import json

@api_view(['GET'])
@permission_classes([AllowAny])
def amazon_callback(request):
    """
    亚马逊授权回调，自动用code换取token。
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    if not code:
        return Response({'error': '缺少code参数'}, status=400)
    client_id = getattr(settings, 'AMAZON_CLIENT_ID', 'your_amazon_client_id')
    client_secret = getattr(settings, 'AMAZON_CLIENT_SECRET', 'your_amazon_client_secret')
    redirect_uri = getattr(settings, 'AMAZON_REDIRECT_URI', 'https://yourdomain.com/api/Amazon/callback')
    token_url = 'https://api.amazon.com/auth/o2/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(token_url, data=data, headers=headers)
    try:
        token_data = resp.json()
    except Exception:
        token_data = {'error': '解析token响应失败', 'raw': resp.text}
    # 可选：保存token到本地文件
    try:
        with open('Datas/AmazonDatas/token_storage_amazon.json', 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        token_data['file_save_error'] = str(e)
    return Response(token_data) 