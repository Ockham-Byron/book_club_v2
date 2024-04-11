from django import forms
from django.utils.translation import gettext_lazy as _
from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput
from .models import Meeting, Comment, Book
from groups.models import CustomGroup



class BookSearch(forms.Form):
    search = forms.CharField(
        label="Search for a book", required=False, widget=forms.TextInput(attrs={'class':  "searchbar", 'id': 'search', 'placeholder': _('Search for a book')}))
    
class AddMeetingForm(forms.ModelForm):
    class Meta:
        model=Meeting
        fields=[  'place']
        widgets= {
            "place":forms.TextInput(attrs={'placeholder': _('Meeting place')})
        }

class AddCommentForm(forms.ModelForm):
    CHOICES = [(i,i) for i in range(6)]
    message=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'placeholder': _("Comment")}))
    rating=forms.TypedChoiceField(coerce=int, choices=CHOICES)

    class Meta:
        model=Comment
        fields=['message', 'rating']

class AddBookForm(forms.ModelForm):
    cover=forms.ImageField(widget=forms.FileInput, required=False)
    
    

    class Meta:
        model=Book
        fields=['title', 'cover','groups']
    
    def __init__(self, user, *args, **kwargs):
        super(AddBookForm, self).__init__(*args, **kwargs)
        
       