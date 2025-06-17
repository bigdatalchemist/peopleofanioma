# apps/pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
    path('socials/', views.socials, name='socials'),

]
