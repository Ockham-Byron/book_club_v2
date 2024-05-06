from django.urls import path
from .views import *



urlpatterns = [
  path('book-save/<id>', add_book, name="save-book"),
  path('search', new_book_search, name="new-book-search"),

  path('all-books', all_books, name="all-books"),
  path('group-books/<slug:slug>', group_books, name="group-books"),
  path('edit-book/<slug:slug>', edit_book, name="edit-book"),
  path('delete-book-from-group/<slug:slug>', delete_book_from_group, name="delete-book-from-group"),
  path('delete-book/<slug:slug>', delete_book, name="delete-book"),
  path('edit-reading-status/<slug:slug>/<id>', edit_reading_status, name="edit-reading-status"),

  #meetings
  path('add-meeting/<slug>', add_meeting, name="add-meeting"),
  path('search-book-for-meeting/<id>', search_book_for_meeting, name="search-book-for-meeting"),
  path('add-new-book-to-meeting/<id>/<str:isbn>', add_new_book_to_meeting, name="add-new-book-to-meeting"),
  path('edit-meeting/<id>', edit_meeting, name="edit-meeting"),
  path('delete-meeting/<id>', delete_meeting, name="delete-meeting"),

  #book
  path('add-book-custom/', add_custom_book, name="add-book-custom"),
  path('book-detail/<slug:slug>', book_detail, name="book-detail"),
  path('add-new-book-to-group/<slug:slug>', add_new_book_to_group, name="add-new-book-to-group"),
  path('pass-book-to-club/<slug:slug>', pass_book_to_sharing_group, name="pass-book-to-sharing-club"),
  path('pass-book-to-library/<slug:slug>', pass_book_to_library, name="pass-book-to-library"),


  #comments
  path('add-review/<slug:slug>', add_review, name="add-review"),
  path('edit-review/<id>', edit_review, name="edit-review"),
  path('delete-review/<id>', delete_review, name="delete-review"),

  #borrow
  path('toggle-borrowable/', toggle_borrowable, name="toggle-borrowable"),
  path('add-borrow/<id>/<slug:slug>', borrow_book_within_group, name="borrow-within-group"),
  path('add-borrow/<id>', borrow_book_no_group, name="borrow-no-group"),
  path('confirm-borrow/<id>', confirm_borrow, name="confirm-borrow"),
  path('add-reservation/<id>/<slug>', reserve_book_within_group, name="reserve-within-group"),
  path('give-book-back/<id>', give_back, name="give-book-back"),
  # path('confirm-return/<id>', confirm_return, name="confirm-return"),
]