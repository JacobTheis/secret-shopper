from django.urls import path
from . import views

app_name = 'targets'

urlpatterns = [
    # Main listing page
    path('', views.TargetsView.as_view(), name='index'),
    # Create new target
    path('create/', views.TargetCreateView.as_view(), name='create'),
    # View target details
    path('<uuid:pk>/', views.TargetDetailView.as_view(), name='detail'),
    # Update existing target
    path('<uuid:pk>/update/', views.TargetUpdateView.as_view(), name='update'),
    # Delete target
    path('<uuid:pk>/delete/', views.TargetDeleteView.as_view(), name='delete'),
    # URL to trigger the start of a new shop's info gathering phase
    path('<uuid:pk>/start-shop/', views.StartShopView.as_view(), name='start_shop'),
]
