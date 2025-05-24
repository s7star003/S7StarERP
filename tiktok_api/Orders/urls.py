from django.urls import path, re_path
from .views import get_order_list_view, get_order_detail_view, get_price_detail_view
from Tiktok_api.Auth.getAccessToken import tiktok_callback
from Tiktok_api.Auth.getAuthCode import get_tiktok_auth_url
from .getAllOrder import get_all_orders_view
from .getOrderAnalysis import get_order_analysis_view
# from .getBuyerAnalysis import get_buyer_analysis_view  # 已移除
# from .go_chat_query import go_chat_query_view  # 已移除
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .getOrderList import get_order_list_view, get_order_list_view_get
from Tiktok_api.Auth.RefreshToken import refresh_token_view

schema_view = get_schema_view(
   openapi.Info(
      title="S7StarERP API",
      default_version='v1',
      description="本地API文档与测试",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('order/list/', get_order_list_view, name='get_order_list'),
    path('order/list_get/', get_order_list_view_get, name='get_order_list_get'),
    path('order/detail/', get_order_detail_view, name='get_order_detail'),
    path('order/price_detail/', get_price_detail_view, name='get_price_detail'),
    path('order/all/', get_all_orders_view, name='get_all_orders'),
    path('order/analysis/', get_order_analysis_view, name='get_order_analysis'),
    # path('buyer/analysis/', get_buyer_analysis_view, name='get_buyer_analysis'),  # 已移除
    # path('go_chat_query/', go_chat_query_view, name='go_chat_query'),  # 已移除
    path('callback', tiktok_callback, name='tiktok_callback'),
    path('auth_url/', get_tiktok_auth_url, name='get_tiktok_auth_url'),
    path('refresh_token', refresh_token_view, name='refresh_token_view'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
