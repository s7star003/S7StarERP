from django.urls import path
from .Auth.callback import miravia_callback

urlpatterns = [
    path('callback', miravia_callback),
] 