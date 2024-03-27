from django import forms
from django.utils.translation import gettext_lazy as _
from bootstrap_datepicker_plus.widgets import DatePickerInput
from .models import Meeting, Book
from groups.models import CustomGroup



class BookSearch(forms.Form):
    search = forms.CharField(
        label="Search for a book", required=False, widget=forms.TextInput(attrs={'class':  "searchbar", 'id': 'search', 'placeholder': _('Search for a book')}))
    
class AddMeetingForm(forms.ModelForm):
    meeting_at = forms.DateField(widget=DatePickerInput(options={
        "format": "DD/MM/YYYY",
        "showTodayButton": True,
        },
        attrs={'class': "input-date"}))
    

    place = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Meeting place')}), required=False)

    class Meta:
        model=Meeting
        fields=[ 'meeting_at', 'place']
    