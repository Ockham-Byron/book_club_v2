from django.urls import path
from .views import *



urlpatterns = [
  path('book-search-details/<id>', book_search_detail, name="book-search-details"),
  path('search', new_book_search, name="new-book-search"),
]