from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.ShopsView.as_view(), name='index'),
    path('cancel/<int:shop_id>/', views.CancelShopView.as_view(), name='cancel'),
    path('results/<int:shop_id>/', views.ShopResultView.as_view(), name='results'),
]
