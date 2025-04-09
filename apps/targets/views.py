from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone # Import timezone
from .models import Target
from .forms import TargetForm
# Import the necessary models from the 'shops' app
from apps.shops.models import Shop, ShopResult, CommunityInfo, Amenity, CommunityPage, FloorPlan
# Import the Celery task for starting information gathering
from apps.shops.tasks import start_information_gathering_task


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
        ).order_by('-updated_at').first() # Order by update timestamp to get the latest

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


class StartShopView(LoginRequiredMixin, View):
    """Handles the request to start the information gathering phase for a target."""
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def post(self, request, *args, **kwargs):
        target_pk = kwargs.get('pk')
        target = get_object_or_404(Target, pk=target_pk)

        # Check if an info gathering shop is already in progress for this target
        # You might want to refine this logic based on your exact requirements
        # (e.g., allow restarting, check for recent failures, etc.)
        existing_shop = Shop.objects.filter(
            target=target,
            status__in=[Shop.Status.PENDING, Shop.Status.IN_PROGRESS]
        ).first()

        if existing_shop:
            messages.warning(request, f"An information gathering process is already running or pending for '{target.name}'.")
        else:
            # Create a new shop instance
            new_shop = Shop.objects.create(
                target=target,
                user=request.user, # Associate with the user initiating the shop
                status=Shop.Status.PENDING # Start as pending, task will update
                # created_at and updated_at fields are auto-populated
            )

            # Trigger the asynchronous task
            start_information_gathering_task.delay(new_shop.id)

            messages.success(request, f"Started information gathering for '{target.name}'. This may take a few minutes.")

        # Redirect back to the target detail page
        return redirect('targets:detail', pk=target.pk)

    def get(self, request, *args, **kwargs):
        # Handle GET requests by redirecting away or showing an error,
        # as this action should only be triggered by POST.
        target_pk = kwargs.get('pk')
        messages.error(request, "Invalid request method.")
        return redirect('targets:detail', pk=target_pk)
