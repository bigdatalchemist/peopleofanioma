# peopleofanioma/backend/anioma_core/urls.py
"""
URL configuration for anioma_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import sitemaps
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('dashboard/', include('apps.dashboards.urls', namespace='dashboard')),
    path("blog/", include("apps.blog.urls")),
    # Correct (redirects to dashboard):
    path("", lambda request: redirect("dashboard/", permanent=False)),
    path("maps/", include("apps.maps.urls")),
    path("diaspora/", include("apps.diaspora_tracker.urls", namespace='diaspora')),
    path("users/", include("apps.users.urls")),
    path('survey/', include('apps.ethnographic_survey.urls')),
    path('stories/', include('apps.stories.urls')),
    path('info/', include('apps.pages.urls')),



    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),



    # Live-reload endpoint for django_browser_reload
    path("__reload__/", include("django_browser_reload.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
