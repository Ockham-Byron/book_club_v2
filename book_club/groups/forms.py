from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import CustomGroup

User=get_user_model()



class AddGroupForm(forms.ModelForm):
    
    kname = forms.CharField(max_length=100, 
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': _("Club's Name"),                    
                                    }))
    
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': _("Description"),
                                                            }), required=False)
    
    
    class Meta:
        model = CustomGroup
        fields = ['kname', 'description']

class UpdateGroupForm(forms.ModelForm):
    kname = forms.CharField(max_length=100, 
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': _("Club's Name"),
                                                            
                                    }))
    group_pic = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}), required=False)

    leader = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    
    class Meta:
        model = CustomGroup
        fields = ['kname', 'group_pic', 'leader']

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        
        super(UpdateGroupForm, self).__init__(*args, **kwargs)
        self.fields['leader'].queryset=User.objects.filter(group_members__uuid = group.uuid)
