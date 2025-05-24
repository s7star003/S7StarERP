from django.urls import path
from .BuyerAnalysis import get_buyer_analysis
from .getAreaDemand_7d import get_area_demand_7d
from .getProfitAnalysis import get_profit_analysis
from .getRepurchaseRate import get_repurchase_rate
from .getReturnRate import get_return_rate
from .getAreaDemand_all import get_area_demand_all
from .getAreaDemand_30d import get_area_demand_30d
from .getSalesRank_all import get_sales_rank_all
from .getSalesRank_30d import get_sales_rank_30d
from .getSalesRank_7d import get_sales_rank_7d

urlpatterns = [
    path('BuyerAnalysis/', get_buyer_analysis, name='get_buyer_analysis'),
    path('AreaDemand_7d/', get_area_demand_7d, name='get_area_demand_7d'),
    path('ProfitAnalysis/', get_profit_analysis, name='get_profit_analysis'),
    path('RepurchaseRate/', get_repurchase_rate, name='get_repurchase_rate'),
    path('ReturnRate/', get_return_rate, name='get_return_rate'),
    path('AreaDemand_all/', get_area_demand_all, name='get_area_demand_all'),
    path('AreaDemand_30d/', get_area_demand_30d, name='get_area_demand_30d'),
    path('SalesRank_all/', get_sales_rank_all, name='get_sales_rank_all'),
    path('SalesRank_30d/', get_sales_rank_30d, name='get_sales_rank_30d'),
    path('SalesRank_7d/', get_sales_rank_7d, name='get_sales_rank_7d'),
] 