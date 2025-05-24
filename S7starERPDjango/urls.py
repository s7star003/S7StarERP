from django.contrib import admin
from django.urls import path, include

DEBUG = True

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/TikTok/', include('Tiktok_api.Orders.urls')),
    path('api/TikTok/DataScience/', include('Tiktok_api.DataScience.urls')),
    path('api/Shein/', include('Shein_api.urls')),
]
