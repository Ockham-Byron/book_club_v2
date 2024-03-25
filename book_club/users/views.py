from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordContextMixin
from django.views.generic.edit import FormView
from .forms import *


from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token

import os

User = get_user_model()

# send email with verification link
def verify_email(request):
    if request.method == "POST":
        if request.user.email_is_verified != True:
            current_site = get_current_site(request)
            user = request.user
            email = request.user.email
            subject = _("Verify Email")
            message = render_to_string('users/authentication/emails/verify_email_message.html', {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            email = EmailMessage(
                subject, message, to=[email]
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('verify-email-done')
        else:
            return redirect('signup')
    
    context = {
        'user': request.user,
    }
    return render(request, 'users/authentication/verify_email.html', context=context)

def verify_email_done(request):
    user = request.user
    email = user.email
    context = {'user': user, 'email': email}
    return render(request, 'users/authentication/verify_email_done.html', context=context)

def verify_email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        return redirect('verify-email-complete')   
    else:
        messages.warning(request, 'The link is invalid. Please register again.')
        print('pas marché')
        return redirect('register')
    

def verify_email_complete(request):
    return render(request, 'users/authentication/verify_email_complete.html')

def change_email(request):
    user = request.user
    form = UserUpdateEmailForm()
    if request.method == 'POST':
        form = UserUpdateEmailForm(request.POST, instance=user)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('verify-email')
    
    context = {'form': form}
    return render(request, 'users/authentication/change_email.html', context=context)


# Create your views here.
def home_view(request):
    return render(request, 'users/home.html')



def login_view(request):
    # Logged in user can't register a new account
    if request.user.is_authenticated:
        return redirect("all-meals")
    
    login_form = UserLoginForm(request.POST)
    

    if request.method == 'POST':
            login_form = UserLoginForm(request=request, data=request.POST)
            if login_form.is_valid():
                user = authenticate(
                    username=login_form.cleaned_data['username'],
                    password=login_form.cleaned_data['password'],
                )
                if user is not None:
                    login(request, user)
                    remember_me = login_form.cleaned_data.get('remember_me')
                    if not remember_me:
                        # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
                        request.session.set_expiry(0)
                    # Set session as modified to force data updates/cookie to be saved.
                    request.session.modified = True
                    if user.email_is_verified:
                        return redirect('dashboard')
                    else:
                        return redirect('verify-email')

                else:
                    for error in list(login_form.errors.values()):
                        messages.error(request, error)
            
    context = {
        'login_form': login_form,
       
    }

    return render(request, 'users/authentication/login.html', context=context)


def register_view(request):
    # Logged in user can't register a new account
    if request.user.is_authenticated:
        return redirect("/")
    
    register_form = UserRegistrationForm(request.POST)
    
    if request.method == 'POST':
        register_form = UserRegistrationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            password = register_form.cleaned_data['password2']
            user.set_password(password)
            user.username = user.email
            user.save()
            new_user = authenticate(username=user.email, password=password)
            login(request, new_user)
            return redirect('verify-email')
        else:
            for error in list(register_form.errors.values()):
                print(request, error)
    
    else:
        register_form = UserRegistrationForm()

    context = {
        'register_form': register_form,
    }

    return render(request, 'users/authentication/register.html', context=context)


                                     

@login_required
def custom_logout(request):
    logout(request)
    
    return render(request, "users/authentication/logout.html")

class PasswordResetCustomView(PasswordContextMixin, FormView):
    email_template_name = 'registration/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    title = _('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            email_template = 'users/authentication/emails/password_reset_email.html'
        
            
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': email_template,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': email_template,
                'extra_email_context': self.extra_email_context,
            }
            form.save(**opts)
            return super().form_valid(form)
        
        else:
            current_site = get_current_site(self.request)
            email = email
            subject = _('Password reset on App')
            message = render_to_string('users/authentication/emails/create_account_email.html', {
                'request': self.request,
                'domain': current_site.domain,
            })
            email = EmailMessage(
                subject, message, to=[email]
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('password_reset_done')
            
    
    


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'

class PasswordResetConfirmCustomView(PasswordContextMixin, FormView):
    form_class = UserUpdatePasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            redirect('login')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context

@login_required
def profile(request, slug):
    user = get_object_or_404(User, slug=slug)
    
    return render(request, 'users/profile.html', {'user': user})


@login_required
def profile_update(request, slug):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been successfully updated '))
            return redirect(to='profile', slug=slug)
        else:
            for error in list(form.errors.values()):
                print(request, error)
            
    
    else:
        form = UserUpdateForm(instance=request.user)
        

    return render(request, 'users/profile_update.html', {'form':form})

@login_required
def delete_profile_pic(request, slug):
    os.remove(request.user.profile_pic.path)
    request.user.profile_pic.delete()
    return redirect(to='profile', slug=slug)

@login_required
def change_avatar(request, slug):
    if request.method == 'POST':
        color = request.POST.get('avatar-color')
        request.user.avatar_color = color
        request.user.save()
        return redirect(to='profile', slug=slug)
        
    return render(request, 'users/choose_avatar.html')

@login_required 
def delete_account(request):
    os.remove(request.user.profile_pic.path)
    request.user.profile_pic.delete()
    request.user.delete()
    return redirect(to="bye")

@login_required
def register_view_from_guest(request, slug):

    user = get_object_or_404(User, slug=slug)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_guest = False
            user.save()
            messages.success(request, _('Your profile has been successfully created '))
            logout(request)
            return redirect(to='login')
        else:
            for error in list(form.errors.values()):
                print(request, error)
            
    
    else:
        form = UserUpdateForm(instance=user)
        

    return render(request, 'users/profile_update.html', {'form':form, 'user':user})