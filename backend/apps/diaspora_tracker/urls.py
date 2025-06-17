from django.urls import path
from . import views

app_name = 'diaspora'
urlpatterns = [
    path('', views.dashboard, name='diaspora_dashboard'),
    path('submit/', views.submit_entry, name='diaspora_submit'),
    path('thank-you/', views.thank_you, name='diaspora_thank_you'),
    path('export/<str:file_format>/', views.export_data, name='export_data'),
]
