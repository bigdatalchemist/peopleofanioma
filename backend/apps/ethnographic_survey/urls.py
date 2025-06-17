# ethnographical_survey/urls.py
from django.urls import path
from . import views
from .views import correlation_heatmap

app_name='ethnographic_survey'
urlpatterns = [
    path('survey_form/', views.survey_form, name='submit_survey'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/<str:file_format>/', views.export_surveys, name='export_surveys'),
    path('correlation/', correlation_heatmap, name='correlation_heatmap'),
    path('keyword_analysis/', views.wordcloud_and_tfidf, name='wordcloud_and_tfidf'),
    path('topic-modeling/', views.topic_modeling_view, name='topic_modeling'),

]
