from django.contrib import admin

from .models import Book, Meeting

# Register your models here.


class BookAdmin(admin.ModelAdmin):
  list_display = ('title',)
  
admin.site.register(Book, BookAdmin)

class MeetingAdmin(admin.ModelAdmin):
  list_display = ('group', 'meeting_at', 'book')

admin.site.register(Meeting, MeetingAdmin)
