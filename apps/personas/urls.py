    from django.urls import path
    from . import views

    app_name = 'personas'

    urlpatterns = [
        path('', views.PersonasView.as_view(), name='index'),
        # Add other persona-related URLs here (e.g., create, detail, update, delete)
    ]
