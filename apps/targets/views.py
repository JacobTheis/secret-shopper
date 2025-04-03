from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Target
from .forms import TargetForm


class TargetsView(LoginRequiredMixin, ListView):
    """Targets main view displaying a list of target properties.

    Requires authenticated user.
    """

    model = Target
    template_name = 'targets/index.html'
    context_object_name = 'targets'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Targets'
        return context


class TargetDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single target property."""

    model = Target
    template_name = 'targets/detail.html'
    context_object_name = 'target'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'


class TargetCreateView(LoginRequiredMixin, CreateView):
    """Create view for a new target property."""

    model = Target
    form_class = TargetForm
    template_name = 'targets/form.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    # success_url = reverse_lazy('targets:index') # Removed: Redirect handled by get_success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Target'
        context['action'] = 'Create'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Target created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the detail view of the newly created target."""
        return reverse_lazy('targets:detail', kwargs={'pk': self.object.pk})


class TargetUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for an existing target property."""

    model = Target
    form_class = TargetForm
    template_name = 'targets/form.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    # success_url = reverse_lazy('targets:index') # Removed: Redirect handled by get_success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Target'
        context['action'] = 'Update'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Target updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the detail view of the updated target."""
        return reverse_lazy('targets:detail', kwargs={'pk': self.object.pk})


class TargetDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for removing a target property."""

    model = Target
    template_name = 'targets/confirm_delete.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    success_url = reverse_lazy('targets:index')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Target deleted successfully.')
        return super().delete(request, *args, **kwargs)
