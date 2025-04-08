from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Target
from .forms import TargetForm
# Import the necessary models from the 'shops' app
from apps.shops.models import Shop, ShopResult, CommunityInfo, Amenity, CommunityPage, FloorPlan


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
    """Detail view for a single target property, including latest shop results."""

    model = Target
    # Ensure this template path is correct for your project structure
    template_name = 'targets/target_detail.html'
    context_object_name = 'target'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        """Add latest completed shop results to the context."""
        context = super().get_context_data(**kwargs)
        target = self.object
        latest_shop_info = None
        latest_completed_shop = None

        # Find the most recent completed shop for this target
        # Ordering by 'end_time' descending assumes end_time is reliably set on completion.
        # You could also use '-created_at' or another relevant timestamp.
        latest_completed_shop = Shop.objects.filter(
            target=target,
            status=Shop.Status.COMPLETED
        ).order_by('-end_time').first()

        if latest_completed_shop:
            try:
                # Attempt to retrieve the linked ShopResult and CommunityInfo
                # This assumes a OneToOne or ForeignKey relationship structure like:
                # Shop -> ShopResult -> CommunityInfo
                # Adjust the access path if your models are linked differently.
                if hasattr(latest_completed_shop, 'shopresult') and \
                   hasattr(latest_completed_shop.shopresult, 'communityinfo'):
                    latest_shop_info = latest_completed_shop.shopresult.communityinfo
                # Example alternative if CommunityInfo has a ForeignKey to ShopResult:
                # elif CommunityInfo.objects.filter(shop_result__shop=latest_completed_shop).exists():
                #    latest_shop_info = CommunityInfo.objects.get(shop_result__shop=latest_completed_shop)

            except (ShopResult.DoesNotExist, CommunityInfo.DoesNotExist, AttributeError):
                # Handle cases where related objects might be missing or relationships aren't set up
                # as expected (e.g., shop completed but results processing failed).
                latest_shop_info = None
                # Optionally add logging here for debugging missing related objects
                # logger.warning(f"Could not find complete shop results for Shop ID {latest_completed_shop.id}")


        context['title'] = f'Target Details: {target.name}' # Add a title for the page
        context['latest_completed_shop'] = latest_completed_shop
        context['latest_shop_info'] = latest_shop_info
        return context


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
        # Ensure the name 'detail' matches the name in your targets/urls.py
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
        # Ensure the name 'detail' matches the name in your targets/urls.py
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
