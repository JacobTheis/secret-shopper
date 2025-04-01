from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.ShopsView.as_view(), name='index'),
]
from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.ShopsView.as_view(), name='index'),
]
