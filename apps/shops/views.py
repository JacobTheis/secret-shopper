from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404

from .models import Shop, ShopResult


class ShopsView(LoginRequiredMixin, TemplateView):
    """Shops main view. Requires authenticated user."""
    template_name = 'shops/index.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Shops'
        shops = Shop.objects.filter(
            user=self.request.user).select_related('target')
        context['shops'] = shops
        return context


class CancelShopView(LoginRequiredMixin, View):
    """View to cancel a shop in progress."""
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def post(self, request, shop_id):
        shop = get_object_or_404(Shop, id=shop_id, user=request.user)

        # Only allow cancellation if shop is pending or in progress
        if shop.status in [Shop.Status.PENDING, Shop.Status.IN_PROGRESS]:
            shop.status = Shop.Status.ERROR
            shop.save(update_fields=['status', 'updated_at'])
            msg = f'Shop for {shop.target.name} has been cancelled.'
            messages.success(request, msg)
        else:
            messages.error(request, 'This shop cannot be cancelled.')

        return redirect('shops:index')


class ShopResultView(LoginRequiredMixin, DetailView):
    """View to display detailed results of a completed shop."""
    template_name = 'shops/result.html'
    context_object_name = 'shop'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_object(self):
        shop_id = self.kwargs.get('shop_id')
        shop = get_object_or_404(Shop, id=shop_id, user=self.request.user)

        # Check if shop is completed and has results
        if shop.status != Shop.Status.COMPLETED:
            raise Http404("Shop has not been completed yet.")

        try:
            # Ensure ShopResult exists
            shop.result
        except ShopResult.DoesNotExist:
            raise Http404("Shop results not found.")

        return shop

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Results for {self.object.target.name}'
        return context
