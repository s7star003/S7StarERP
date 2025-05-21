from django.urls import path
from .getAuthCode import tiktok_callback

urlpatterns = [
    path('callback/', tiktok_callback, name='tiktok_callback'),
]
