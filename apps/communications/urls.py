    from django.urls import path
    from . import views

    app_name = 'communications'

    urlpatterns = [
        path('', views.CommunicationsView.as_view(), name='index'),
        # Add other communication-related URLs here
    ]
