from django.contrib import admin
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils.translation import gettext as _
from .models import CustomUser

# Register your models here.
class WithinSixMonthsActivityFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Activity within six months")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "decade"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("yes", _("Active")),
            ("no", _("Inactive")),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        six_months_ago = datetime.now() - timedelta(days=180)
        
        if self.value() == "yes":
            
            return queryset.filter(
                last_login__gte=six_months_ago
                
            )
        if self.value() == "no":
            return queryset.filter(
                last_login__lte=six_months_ago
                
            )
        
class CustomUserAdmin(admin.ModelAdmin):
  list_display=('pseudo', 'first_name', 'last_name', 'email', 'created_at', 'updated_at', 'last_login')
  list_filter = [WithinSixMonthsActivityFilter]

admin.site.register(CustomUser, CustomUserAdmin)