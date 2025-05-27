from django.urls import path
from .getAuthCode import get_amazon_auth_url
from .callback import amazon_callback
from .refreshToken import refresh_amazon_token

urlpatterns = [
    path('getAuthCode/', get_amazon_auth_url, name='amazon_get_auth_code'),
    path('callback/', amazon_callback, name='amazon_callback'),
    path('refreshToken/', refresh_amazon_token, name='amazon_refresh_token'),
] 