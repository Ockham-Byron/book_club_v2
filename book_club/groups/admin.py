from django.contrib import admin
from django.db.models import Count
from .models import CustomGroup

# Register your models here.


class CustomGroupAdmin(admin.ModelAdmin):
  list_display = ('name', 'leader', 'created_at', 'updated_at', 'members_count')
  

  def members_count(self, obj):
        return len(obj.members.all()) + 1
  
  members_count.short_description = 'Members'
  members_count.admin_order_field = 'members_count'

  def get_queryset(self, *args, **kwargs):
    return super().get_queryset(*args, **kwargs).annotate(members_count = Count("members"))

admin.site.register(CustomGroup, CustomGroupAdmin)
