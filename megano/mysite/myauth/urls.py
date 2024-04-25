from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import (
    SignInView,
    SignUpView,
    ProfileView,
    AvatarUploadView,
    ChangeUserPassword,
)

urlpatterns = [
    path('sign-in', SignInView.as_view(), name='sign-in'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/avatar', AvatarUploadView.as_view(), name='avatar'),
    path('profile/password', ChangeUserPassword.as_view(), name='change-password'),
]
