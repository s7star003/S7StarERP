from django.contrib import admin
from django.urls import path, include

DEBUG = True

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/TikTok/', include('Tiktok_api.urls')),
    path('api/Shein/', include('Shein_api.urls')),
    path('api/Miravia/', include('Miravia_api.urls')),
]
