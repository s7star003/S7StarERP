import os
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="获取Miravia退货率分析数据",
    responses={200: openapi.Response('返回Miravia退货率分析数据')},
    tags=['Miravia']
)
@api_view(['GET'])
def get_return_rate(request):
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'MultiplatformDataDashboardDataSource', 'Miravia', 'ReturnRate.json'
    )
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Response({'code': 0, 'msg': 'success', 'data': data})
    except Exception as e:
        return Response({'code': 1, 'msg': 'error', 'error': str(e)}, status=500) 