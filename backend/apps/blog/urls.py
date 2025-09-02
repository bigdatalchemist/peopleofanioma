from django.urls import path
from . import views
from .views import blog_search

app_name = "blog"

urlpatterns = [
    path('', views.blog_list, name='blog_list'),

    # Specific routes FIRST
    path('search/', blog_search, name='blog_search'),
    path('videos/', views.video_list, name='video_list'),
    path('videos/<slug:slug>/', views.video_detail, name='video_detail'),
    path('<int:post_id>/react/', views.add_reaction, name='add_reaction'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),

    # Catch-all slug LAST
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]
