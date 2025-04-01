from django.urls import path
from . import views

urlpatterns = [
    path('', views.ShopsView.as_view(), name='index'),
]
