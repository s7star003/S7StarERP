from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import json

@swagger_auto_schema(method='get', tags=['Shein'])
@api_view(['GET'])
def get_area_demand_all(request):
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'MultiplatformDataDashboardDataSource', 'Shein', 'AreaDemand_all.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Response({'code': 0, 'msg': 'success', 'data': data})
    except Exception as e:
        return Response({'code': 1, 'msg': 'error', 'error': str(e)}, status=500) 