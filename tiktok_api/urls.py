from django.urls import path
from .views import get_order_list_view, get_order_detail_view

urlpatterns = [
    path('getorderlist', get_order_list_view),
    path('getorderdetail', get_order_detail_view),
]
