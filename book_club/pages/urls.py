from django.urls import path
from .views import *



urlpatterns = [
  path('bye/', bye_page, name="bye"),
  
]