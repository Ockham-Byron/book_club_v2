from django.urls import path
from .views import *



urlpatterns = [
  path('book-save/<id>', add_book, name="save-book"),
  path('search', new_book_search, name="new-book-search"),

  path('all-books', all_books, name="all-books"),
  path('group-books/<slug:slug>', group_books, name="group-books"),
  path('edit-book/<slug:slug>', edit_book, name="edit-book"),
  path('delete-book/<slug:slug>', delete_book, name="delete-book"),
  path('edit-reading-status/<slug:slug>/<id>', edit_reading_status, name="edit-reading-status"),

  #meetings
  path('add-meeting/<slug>', add_meeting, name="add-meeting"),
  path('search-book-for-meeting/<id>', search_book_for_meeting, name="search-book-for-meeting"),
  path('add-new-book-to-meeting/<id>/<str:isbn>', add_new_book_to_meeting, name="add-new-book-to-meeting"),
  path('edit-meeting/<id>', edit_meeting, name="edit-meeting"),

  #book
  path('add-book-custom/', add_custom_book, name="add-book-custom"),
  path('book-detail/<slug:slug>', book_detail, name="book-detail"),
  path('add-new-book-to-group/<slug:slug>', add_new_book_to_group, name="add-new-book-to-group"),

  #comments
  path('add-review/<slug:slug>', add_review, name="add-review"),
]