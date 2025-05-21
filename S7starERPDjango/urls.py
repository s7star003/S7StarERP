from django.contrib import admin
from django.urls import path, include

DEBUG = True

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/TikTok/', include('tiktok_api.urls')),
]
