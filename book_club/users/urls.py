from django.urls import path
from .views import *

from django.contrib.auth.views import (
    PasswordResetDoneView, 
    PasswordResetCompleteView
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', custom_logout, name='logout'),

    #verify email urls
    path('verify-email/', verify_email, name='verify-email'),
    path('verify-email/done/', verify_email_done, name='verify-email-done'),
    path('verify-email-confirm/<uidb64>/<token>/', verify_email_confirm, name='verify-email-confirm'),
    path('verify-email/complete/', verify_email_complete, name='verify-email-complete'),
    path('verify-email/change-email/', change_email, name='change-email'),

    #password reset
    path('password-reset/', PasswordResetCustomView.as_view(template_name='users/authentication/password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/authentication/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmCustomView.as_view(template_name='users/authentication/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='users/authentication/password_reset_complete.html'),name='password_reset_complete'),

   

    #profile url
    path('profile/<slug:slug>', profile, name='profile'),
    path('profile/<slug:slug>/update', profile_update, name='profile-update'),
    path('profile/<slug:slug>)/update/delete-profile-pic', delete_profile_pic, name='profile-pic-delete'),
    path('profile/<slug:slug>/update/avatar-color', change_avatar, name='change-avatar'),
    path('create-account-from-guest/<slug:slug>', register_view_from_guest, name='create-account-from-guest')
    
] 