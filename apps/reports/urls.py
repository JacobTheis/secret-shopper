from django.urls import path
from . import views

app_name = 'apps.reports'

urlpatterns = [
    path('', views.ReportsView.as_view(), name='index'),
]
