from django.urls import path
from . import views

app_name = 'targets'

urlpatterns = [
    path('', views.TargetsView.as_view(), name='index'),
]
