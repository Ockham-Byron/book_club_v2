from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate, password_validation
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()
AVATAR_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
    )


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(error_messages={
                                'unique': _("A user with that email already exists. If you have lost your password, please go to Login and Forgot password."),},
                            widget=forms.EmailInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Email')}),
                            )
    pseudo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Username'), 'autocomplete':"username"}),)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Password'), 'autocomplete': "new-password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Repeat Password'), 'autocomplete': 'new-password'}))
    is_rgpd = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['pseudo', 'email', 'password1', 'password2', 'is_rgpd']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    



    
class UserLoginForm(AuthenticationForm):

    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Email')}),)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Password'), 'data-toggle': 'password',}))
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username = username, password=password)
        if not user:
            if User.objects.filter(email=username).exists():
                message = _("This isn't the password registered with %(email)s. If you don't remember your password, please click on 'Forgot Password' .") % {'email':username}
                raise forms.ValidationError(message)
            else:
                message = _("No user registered with %(email)s...") % {'email': username}
                raise forms.ValidationError(message)
        
        
        return self.cleaned_data
    
    
    
    
class UserUpdateEmailForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Email')}),)
    class Meta:
        model = User
        fields = ['email']


class UserUpdatePasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'data-toggle': 'password',}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'data-toggle': 'password',}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
    
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':_('First Name')}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':_('Last Name')}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={ 'placeholder': _('Email')}),required=False)
    pseudo = forms.CharField(widget=forms.TextInput(attrs={'placeholder':_('Pseudo')}), required=False)
    profile_pic = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder':_('Bio'), 'rows': 5}), required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_pic', 'bio', 'pseudo']

