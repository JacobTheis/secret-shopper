from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportsView.as_view(), name='index'),
]
