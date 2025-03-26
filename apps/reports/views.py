from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ReportsView(LoginRequiredMixin, TemplateView):
    """Reports main view. Requires authenticated user."""
    
    template_name = 'reports/index.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reports'
        return context
