from django.urls import path
from .Auth.callback import miravia_callback
# DataScience
from Miravia_api.DataScience.getSalesRank_7d import get_sales_rank_7d
from Miravia_api.DataScience.getSalesRank_30d import get_sales_rank_30d
from Miravia_api.DataScience.getSalesRank_all import get_sales_rank_all
from Miravia_api.DataScience.getAreaDemand_7d import get_area_demand_7d
from Miravia_api.DataScience.getAreaDemand_30d import get_area_demand_30d
from Miravia_api.DataScience.getAreaDemand_all import get_area_demand_all
from Miravia_api.DataScience.getRepurchaseRate import get_repurchase_rate
from Miravia_api.DataScience.getReturnRate import get_return_rate
from Miravia_api.DataScience.getProfitAnalysis import get_profit_analysis
from Miravia_api.DataScience.getMonthlySalesAnalysis import get_monthly_sales_analysis
from Miravia_api.DataScience.BuyerAnalysis import get_buyer_analysis
from Miravia_api.DataScience.OrderAnalysis import get_order_analysis

urlpatterns = [
    path('callback', miravia_callback),
    # DataScience
    path('DataScience/getSalesRank_7d/', get_sales_rank_7d, name='get_sales_rank_7d'),
    path('DataScience/getSalesRank_30d/', get_sales_rank_30d, name='get_sales_rank_30d'),
    path('DataScience/getSalesRank_all/', get_sales_rank_all, name='get_sales_rank_all'),
    path('DataScience/getAreaDemand_7d/', get_area_demand_7d, name='get_area_demand_7d'),
    path('DataScience/getAreaDemand_30d/', get_area_demand_30d, name='get_area_demand_30d'),
    path('DataScience/getAreaDemand_all/', get_area_demand_all, name='get_area_demand_all'),
    path('DataScience/getRepurchaseRate/', get_repurchase_rate, name='get_repurchase_rate'),
    path('DataScience/getReturnRate/', get_return_rate, name='get_return_rate'),
    path('DataScience/getProfitAnalysis/', get_profit_analysis, name='get_profit_analysis'),
    path('DataScience/getMonthlySalesAnalysis/', get_monthly_sales_analysis, name='get_monthly_sales_analysis'),
    path('DataScience/getBuyerAnalysis/', get_buyer_analysis, name='get_buyer_analysis'),
    path('DataScience/getOrderAnalysis/', get_order_analysis, name='get_order_analysis'),
] 