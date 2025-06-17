# apps/pages/views.py
from django.shortcuts import render

def about(request):
    return render(request, 'pages/about.html')

def terms(request):
    return render(request, 'pages/terms.html')

def contact(request):
    return render(request, 'pages/contact.html')

def socials(request):
    return render(request, 'pages/socials.html')
