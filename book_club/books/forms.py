from django import forms
from django.utils.translation import gettext_lazy as _

class BookSearch(forms.Form):
    search = forms.CharField(
        label="Search for a book", required=False, widget=forms.TextInput(attrs={'class':  "searchbar", 'id': 'search', 'placeholder': _('Search for a book')}))
    