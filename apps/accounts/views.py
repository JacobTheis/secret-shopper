from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CustomLoginView(LoginView):
    """Custom login view that uses Django's built-in AuthenticationForm."""
    
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add Bootstrap classes to form widgets
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['post', 'get']


class RegisterView(FormView):
    """View for user registration."""
    
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard:index')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add Bootstrap classes to form widgets
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().get(*args, **kwargs)
