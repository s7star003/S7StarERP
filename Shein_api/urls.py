from django.urls import path, include
from .Auth.authorize_temp import authorizate_temp
from .Auth.callback import shein_callback
from .Orders.getOrderlists import get_order_lists

urlpatterns = [
    path('authorizateTemp', authorizate_temp),
    path('callback', shein_callback),
    path('orders/getOrderlists', get_order_lists),
    path('DataScience/', include('Shein_api.DataScience.urls')),
] 