from django.urls import path
from .views import *



urlpatterns = [
  path('add-group/', add_group_view, name="add-group"),
  path('my-groups/', all_groups, name="all-groups"),
  path('join-group', join_group_view, name='join-group'),
  path('group-detail/<slug:slug>/update-group', GroupUpdateView.as_view(), name='update-group'),
  path('group-detail/<slug:slug>/', GroupDetailView.as_view(), name='group-detail'), 

  #library
  path('create-library/', add_library_view, name="create-library"),
  path('create-wishlist/', add_wishlist_view, name="create-wishlist"),
  path('my-library/<slug:slug>', LibraryView.as_view(), name="library"),
  path('my-wishlist/<slug:slug>', WishlistView.as_view(), name="wishlist"),
  
]