from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from urllib.parse import urlencode

@api_view(['GET'])
@permission_classes([AllowAny])
def get_amazon_auth_url(request):
    """
    生成亚马逊授权URL，供前端跳转授权。
    """
    # 这些参数请根据你的亚马逊开发者后台实际配置填写
    client_id = getattr(settings, 'AMAZON_CLIENT_ID', 'your_amazon_client_id')
    redirect_uri = getattr(settings, 'AMAZON_REDIRECT_URI', 'https://yourdomain.com/api/Amazon/callback')
    state = 'random_state_string'  # 可根据需要生成
    scope = 'profile'  # 根据需要调整
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'state': state,
        'scope': scope
    }
    base_url = 'https://www.amazon.com/ap/oa?'
    auth_url = base_url + urlencode(params)
    return Response({
        'auth_url': auth_url,
        'message': '请点击链接进行亚马逊授权',
        'link': f'<a href="{auth_url}" target="_blank">点击授权</a>'
    }) 