from django.contrib import admin

from .models import Book, Meeting, Comment, CustomBook, Borrow

# Register your models here.


class BookAdmin(admin.ModelAdmin):
  list_display = ('title',)
  
admin.site.register(Book, BookAdmin)

class CustomBookAdmin(admin.ModelAdmin):
  list_display = ('book', 'owner', 'admin')

admin.site.register(CustomBook, CustomBookAdmin)

class MeetingAdmin(admin.ModelAdmin):
  list_display = ('group', 'meeting_at', 'book')

admin.site.register(Meeting, MeetingAdmin)

class CommentAdmin(admin.ModelAdmin):
  list_display = ('book', 'author', 'rating')

admin.site.register(Comment, CommentAdmin)

class BorrowAdmin(admin.ModelAdmin):
  list_display = ('custom_book', 'borrower', 'borrow_start', 'status')

admin.site.register(Borrow, BorrowAdmin)

