from django.urls import path
from .views import *



urlpatterns = [
  path('add-group/', add_group_view, name="add-group"),
  path('my-groups/', all_groups, name="all-groups"),
  path('join-group', join_group_view, name='join-group'),
  path('group-detail/<pk>/<slug:slug>/update-group', GroupUpdateView.as_view(), name='update-group'),
  path('group-detail/<slug:slug>/', GroupDetailView.as_view(), name='group-detail'), 
  
]