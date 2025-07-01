# stories/urls.py
from django.urls import path
from . import views
from .views import add_story_reaction

app_name = 'stories'
urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('submit/', views.submit_story, name='submit_story'),
    path('thank-you/', views.thank_you, name='story_thank_you'),
    path('user/', views.user_profile, name='user_profile'),
    path('<slug:slug>/', views.story_detail, name='story_detail'),
    path('<int:story_id>/react/', add_story_reaction, name='add_story_reaction'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('<slug:slug>/edit/', views.edit_story, name='edit_story'),
    path('<slug:slug>/delete/', views.delete_story, name='delete_story'),

    
]
