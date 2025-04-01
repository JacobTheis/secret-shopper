from django.urls import path
from . import views

app_name = 'apps.shops'

urlpatterns = [
    path('', views.ShopsView.as_view(), name='index'),
]
