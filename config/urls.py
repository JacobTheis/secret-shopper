"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Include custom accounts views first to override defaults
urlpatterns = [
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
]

# Include default auth views (for password reset, etc.)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += [
    path("admin/", admin.site.urls),
    # Note: The custom accounts path is already included above
    path("personas/", include("apps.personas.urls", namespace="personas")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("targets/", include("apps.targets.urls", namespace="targets")),
    path("communications/", include("apps.communications.urls", namespace="communications")),
    path("shops/", include("apps.shops.urls", namespace="shops")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    # Redirect root to login page
    path("", RedirectView.as_view(pattern_name="accounts:login"), name="home"),
]

# Serve media files in development
if settings.DEBUG:
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # Note: Static files are served automatically by django.contrib.staticfiles
    # when DEBUG=True. No need to add static(settings.STATIC_URL, ...) here.

if settings.DEBUG:
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # Note: Static files are served automatically by django.contrib.staticfiles
    # when DEBUG=True. No need to add static(settings.STATIC_URL, ...) here.
