from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .forms import CustomLoginForm
from .views import (
    update_profile_pic,
    delete_profile_pic,
    edit_bio
)

app_name = 'users'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),
    path(
        'logout/',
        LogoutView.as_view(
            template_name='users/logout.html',
            next_page='users:login',
        ),
        name='logout',
    ),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/picture/update/', update_profile_pic, name='update_profile_pic'),
    path('profile/picture/delete/', delete_profile_pic, name='delete_profile_pic'),
    path('profile/bio/edit/', edit_bio, name='edit_bio'),
]
