from django.urls import path
from .authorize_temp import authorizate_temp
from .callback import shein_callback
 
urlpatterns = [
    path('authorizateTemp', authorizate_temp),
    path('callback', shein_callback),
] 