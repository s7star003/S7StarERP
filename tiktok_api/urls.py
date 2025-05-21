from django.urls import path
from .views import get_order_list_view, get_order_detail_view

urlpatterns = [
    path('getOrderList', get_order_list_view),
    path('getOrderDetail', get_order_detail_view),
]
