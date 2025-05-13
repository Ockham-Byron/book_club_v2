from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('install-app', install_app_view, name='install-app'),
] 