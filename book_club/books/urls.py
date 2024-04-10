from django.urls import path
from .views import *



urlpatterns = [
  path('book-save/<id>', add_book, name="save-book"),
  path('search', new_book_search, name="new-book-search"),

  #meetings
  path('add-meeting/<slug>', add_meeting, name="add-meeting"),
  path('search-book-for-meeting/<id>', search_book_for_meeting, name="search-book-for-meeting"),
  path('add-new-book-to-meeting/<id>/<str:isbn>', add_new_book_to_meeting, name="add-new-book-to-meeting"),

  #book
  path('book-detail/<id>', book_detail, name="book-detail"),
]