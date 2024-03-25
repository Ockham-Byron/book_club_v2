from django.urls import path
from .views import *



urlpatterns = [
  path('search', book_search, name="book-search"),
  path('results', book_results, name="book-results"),
  path('test-search', search, name="search"),
]