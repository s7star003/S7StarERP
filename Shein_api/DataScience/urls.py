from django.urls import path
from .getSalesRank_7d import get_sales_rank_7d
from .getSalesRank_30d import get_sales_rank_30d
from .getSalesRank_all import get_sales_rank_all
from .getAreaDemand_7d import get_area_demand_7d
from .getAreaDemand_30d import get_area_demand_30d
from .getAreaDemand_all import get_area_demand_all
from .getRepurchaseRate import get_repurchase_rate
from .getReturnRate import get_return_rate
from .getProfitAnalysis import get_profit_analysis
from .getMonthlySalesAnalysis import get_monthly_sales_analysis
from .OrderAnalysis import get_order_analysis
from .BuyerAnalysis import get_buyer_analysis

urlpatterns = [
    path('getSalesRank_7d', get_sales_rank_7d),
    path('getSalesRank_30d', get_sales_rank_30d),
    path('getSalesRank_all', get_sales_rank_all),
    path('getAreaDemand_7d', get_area_demand_7d),
    path('getAreaDemand_30d', get_area_demand_30d),
    path('getAreaDemand_all', get_area_demand_all),
    path('getRepurchaseRate', get_repurchase_rate),
    path('getReturnRate', get_return_rate),
    path('getProfitAnalysis', get_profit_analysis),
    path('getMonthlySalesAnalysis', get_monthly_sales_analysis),
    path('getOrderAnalysis', get_order_analysis),
    path('getBuyerAnalysis', get_buyer_analysis),
] 