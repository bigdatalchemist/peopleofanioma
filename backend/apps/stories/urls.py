# stories/urls.py
from django.urls import path
from . import views
app_name = 'stories'
urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('submit/', views.submit_story, name='submit_story'),
    path('thank-you/', views.thank_you, name='story_thank_you'),
    path('user/', views.user_profile, name='user_profile'),
    path('<slug:slug>/', views.story_detail, name='story_detail'),
    path('<slug:slug>/like/', views.like_story, name='like_story'),
    path('<slug:slug>/upvote/', views.upvote_story, name='upvote_story'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    
]
