from django.urls import path, re_path
from Tiktok_api.Orders.views import get_order_list_view, get_order_detail_view, get_price_detail_view
from Tiktok_api.Auth.getAccessToken import tiktok_callback
from Tiktok_api.Auth.getAuthCode import get_tiktok_auth_url
from Tiktok_api.Orders.getAllOrder import get_all_orders_view
from Tiktok_api.Orders.getOrderAnalysis import get_order_analysis_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from Tiktok_api.Orders.getOrderList import get_order_list_view_get
from Tiktok_api.Auth.RefreshToken import refresh_token_view
# DataScience
from Tiktok_api.DataScience.BuyerAnalysis import get_buyer_analysis
from Tiktok_api.DataScience.getAreaDemand_7d import get_area_demand_7d
from Tiktok_api.DataScience.getProfitAnalysis import get_profit_analysis
from Tiktok_api.DataScience.getRepurchaseRate import get_repurchase_rate
from Tiktok_api.DataScience.getReturnRate import get_return_rate
from Tiktok_api.DataScience.getAreaDemand_all import get_area_demand_all
from Tiktok_api.DataScience.getAreaDemand_30d import get_area_demand_30d
from Tiktok_api.DataScience.getSalesRank_all import get_sales_rank_all
from Tiktok_api.DataScience.getSalesRank_30d import get_sales_rank_30d
from Tiktok_api.DataScience.getSalesRank_7d import get_sales_rank_7d

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
    # Orders
    path('order/list/', get_order_list_view, name='get_order_list'),
    path('order/list_get/', get_order_list_view_get, name='get_order_list_get'),
    path('order/detail/', get_order_detail_view, name='get_order_detail'),
    path('order/price_detail/', get_price_detail_view, name='get_price_detail'),
    path('order/all/', get_all_orders_view, name='get_all_orders'),
    path('order/analysis/', get_order_analysis_view, name='get_order_analysis'),
    path('callback', tiktok_callback, name='tiktok_callback'),
    path('auth_url/', get_tiktok_auth_url, name='get_tiktok_auth_url'),
    path('refresh_token', refresh_token_view, name='refresh_token_view'),
    re_path(r'^swagger(?P<format>\\.json|\\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # DataScience
    path('DataScience/BuyerAnalysis/', get_buyer_analysis, name='get_buyer_analysis'),
    path('DataScience/AreaDemand_7d/', get_area_demand_7d, name='get_area_demand_7d'),
    path('DataScience/ProfitAnalysis/', get_profit_analysis, name='get_profit_analysis'),
    path('DataScience/RepurchaseRate/', get_repurchase_rate, name='get_repurchase_rate'),
    path('DataScience/ReturnRate/', get_return_rate, name='get_return_rate'),
    path('DataScience/AreaDemand_all/', get_area_demand_all, name='get_area_demand_all'),
    path('DataScience/AreaDemand_30d/', get_area_demand_30d, name='get_area_demand_30d'),
    path('DataScience/SalesRank_all/', get_sales_rank_all, name='get_sales_rank_all'),
    path('DataScience/SalesRank_30d/', get_sales_rank_30d, name='get_sales_rank_30d'),
    path('DataScience/SalesRank_7d/', get_sales_rank_7d, name='get_sales_rank_7d'),
] 