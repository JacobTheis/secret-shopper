import logging
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
from kombu.exceptions import OperationalError # Add this import

logger = logging.getLogger(__name__)


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
        # You could also use '-updated_at' or another relevant timestamp.
        latest_completed_shop = Shop.objects.filter(
            target=target,
            status=Shop.Status.COMPLETED
        ).order_by('-updated_at').first() # Order by update timestamp to get the latest

        if latest_completed_shop:
            try:
                # Attempt to retrieve the linked ShopResult and CommunityInfo
                # Model relationships: Shop -> ShopResult (result) -> CommunityInfo (community_info)
                if hasattr(latest_completed_shop, 'result') and \
                   hasattr(latest_completed_shop.result, 'community_info'):
                    latest_shop_info = latest_completed_shop.result.community_info
                # Alternative direct lookup if needed
                elif CommunityInfo.objects.filter(shop_result__shop=latest_completed_shop).exists():
                    latest_shop_info = CommunityInfo.objects.get(shop_result__shop=latest_completed_shop)

            except (ShopResult.DoesNotExist, CommunityInfo.DoesNotExist, AttributeError) as e:
                # Handle cases where related objects might be missing or relationships aren't set up
                # as expected (e.g., shop completed but results processing failed).
                latest_shop_info = None
                # Add logging for debugging missing related objects
                logger.warning(f"Could not find community info for Shop ID {latest_completed_shop.id}: {e}")

        # Group fees by source for better organization
        grouped_fees = {}
        if latest_shop_info:
            fees = latest_shop_info.fees.all()
            for fee in fees:
                # Use source URL as the key, or 'Unknown Source' if not available
                source_key = fee.source_url if fee.source_url else 'Unknown Source'
                
                # Extract a friendly name from the URL for display
                if fee.source_url:
                    try:
                        from urllib.parse import urlparse
                        parsed_url = urlparse(fee.source_url)
                        
                        # Create a friendly name from the URL path
                        path_parts = [part for part in parsed_url.path.split('/') if part]
                        
                        # Get the domain name for display
                        domain = parsed_url.netloc or 'unknown'
                        
                        if path_parts:
                            # Use the last meaningful part of the path
                            last_part = path_parts[-1]
                            
                            # Handle common page names and convert to friendly names
                            friendly_names = {
                                'fees': 'Fees Page',
                                'pricing': 'Pricing Page', 
                                'application': 'Application Page',
                                'pet-policy': 'Pet Policy Page',
                                'pet_policy': 'Pet Policy Page',
                                'amenities': 'Amenities Page',
                                'lease': 'Lease Information',
                                'terms': 'Terms & Conditions',
                                'faq': 'FAQ Page',
                                'contact': 'Contact Page'
                            }
                            
                            # Check if we have a specific friendly name
                            last_part_clean = last_part.lower().replace('.html', '').replace('.php', '')
                            if last_part_clean in friendly_names:
                                page_title = friendly_names[last_part_clean]
                            else:
                                # Convert to title case and clean up
                                page_title = last_part.replace('-', ' ').replace('_', ' ').replace('.html', '').replace('.php', '').title()
                                if not page_title.strip():
                                    page_title = 'Main Website'
                            
                            # Format as "Page Title (domain.com)"
                            source_display = f"{page_title} ({domain})"
                        else:
                            # No path, use domain name with "Main Website" title
                            source_display = f"Main Website ({domain})"
                    except Exception:
                        source_display = fee.source_url
                else:
                    source_display = 'Unknown Source'
                
                if source_key not in grouped_fees:
                    grouped_fees[source_key] = {
                        'display_name': source_display,
                        'url': fee.source_url,
                        'fees': []
                    }
                grouped_fees[source_key]['fees'].append(fee)

        context['title'] = f'Target Details: {target.name}' # Add a title for the page
        context['latest_completed_shop'] = latest_completed_shop
        context['latest_shop_info'] = latest_shop_info
        context['grouped_fees'] = grouped_fees
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

            try:
                # Trigger the asynchronous task
                start_information_gathering_task.delay(new_shop.id)
                messages.success(request, f"Started information gathering for '{target.name}'. This may take a few minutes.")
            except OperationalError:
                # If Celery can't connect to the broker (Redis)
                messages.error(request, "Could not start information gathering. The task processing service is currently unavailable. Please try again later or contact an administrator.")
                # Optionally, you might want to change the shop status to FAILED or delete it
                # For example:
                # new_shop.status = Shop.Status.FAILED
                # new_shop.save()
                # or new_shop.delete() 
                # For now, we'll just show an error message. The shop object will remain with PENDING status.

        # Redirect back to the target detail page
        return redirect('targets:detail', pk=target.pk)

    def get(self, request, *args, **kwargs):
        # Handle GET requests by redirecting away or showing an error,
        # as this action should only be triggered by POST.
        target_pk = kwargs.get('pk')
        messages.error(request, "Invalid request method.")
        return redirect('targets:detail', pk=target_pk)


class ExportReportView(LoginRequiredMixin, View):
    """Export target report as PDF."""
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        """Generate and return PDF report for the target."""
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from io import BytesIO
        from datetime import datetime

        target_pk = kwargs.get('pk')
        target = get_object_or_404(Target, pk=target_pk)

        # Get the latest completed shop information
        latest_completed_shop = Shop.objects.filter(
            target=target,
            status=Shop.Status.COMPLETED
        ).order_by('-updated_at').first()

        if not latest_completed_shop:
            messages.error(request, "No completed shop results found for this target.")
            return redirect('targets:detail', pk=target_pk)

        # Get community info
        latest_shop_info = None
        try:
            if hasattr(latest_completed_shop, 'result') and \
               hasattr(latest_completed_shop.result, 'community_info'):
                latest_shop_info = latest_completed_shop.result.community_info
            elif CommunityInfo.objects.filter(shop_result__shop=latest_completed_shop).exists():
                latest_shop_info = CommunityInfo.objects.get(shop_result__shop=latest_completed_shop)
        except (ShopResult.DoesNotExist, CommunityInfo.DoesNotExist, AttributeError):
            latest_shop_info = None

        if not latest_shop_info:
            messages.error(request, "No community information found for this target.")
            return redirect('targets:detail', pk=target_pk)

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        # Container for the 'Flowable' objects
        elements = []

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )

        # Title
        elements.append(Paragraph(f"Secret Shop Report: {target.name}", title_style))
        elements.append(Spacer(1, 12))

        # Report metadata
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        elements.append(Paragraph(f"Shop Completed: {latest_completed_shop.end_time.strftime('%B %d, %Y at %I:%M %p') if latest_completed_shop.end_time else 'N/A'}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Target Information
        elements.append(Paragraph("Target Property Information", heading_style))
        elements.append(Paragraph(f"<b>• Property Name:</b> {target.name}", styles['Normal']))
        elements.append(Paragraph(f"<b>• Address:</b> {f'{target.street_address or ''} {target.city or ''} {target.state or ''} {target.zip_code or ''}'.strip() or 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>• Email:</b> {target.email_address or 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>• Phone:</b> {target.phone_number or 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>• Website:</b> {target.website or 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>• Owner(s):</b> {target.owners or 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>• Property Manager:</b> {target.property_manager or 'N/A'}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Community Information
        elements.append(Paragraph("Community Information", heading_style))
        elements.append(Paragraph(f"<b>Name:</b> {latest_shop_info.name or 'N/A'}", styles['Normal']))
        elements.append(Spacer(1, 6))
        
        if latest_shop_info.overview:
            elements.append(Paragraph(f"<b>Overview:</b> {latest_shop_info.overview}", styles['Normal']))
            elements.append(Spacer(1, 6))
        
        if latest_shop_info.url:
            elements.append(Paragraph(f"<b>Website:</b> {latest_shop_info.url}", styles['Normal']))
            elements.append(Spacer(1, 6))

        # Fees Information
        fees = latest_shop_info.fees.all()
        if fees:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Fees", heading_style))
            
            for fee in fees:
                amount_str = f"${fee.amount}" if fee.amount else "Variable"
                refundable_str = "Yes" if fee.refundable else "No"
                
                elements.append(Paragraph(f"<b>• {fee.name}</b>", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Amount: {amount_str}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Frequency: {fee.get_frequency_display()}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Category: {fee.fee_category or 'N/A'}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Refundable: {refundable_str}", styles['Normal']))
                
                if fee.description:
                    elements.append(Paragraph(f"&nbsp;&nbsp;◦ Description: {fee.description}", styles['Normal']))
                if fee.conditions:
                    elements.append(Paragraph(f"&nbsp;&nbsp;◦ Conditions: {fee.conditions}", styles['Normal']))
                
                elements.append(Spacer(1, 6))

        # Floor Plans
        floor_plans = latest_shop_info.floor_plans.all()
        if floor_plans:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Floor Plans", heading_style))
            
            for plan in floor_plans:
                rent_range = "N/A"
                if plan.min_rental_price and plan.max_rental_price:
                    rent_range = f"${plan.min_rental_price} - ${plan.max_rental_price}"
                elif plan.min_rental_price:
                    rent_range = f"${plan.min_rental_price}"
                elif plan.max_rental_price:
                    rent_range = f"Up to ${plan.max_rental_price}"
                
                deposit = f"${plan.security_deposit}" if plan.security_deposit else "N/A"
                
                elements.append(Paragraph(f"<b>• {plan.name}</b>", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Type: {plan.type or 'N/A'}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Bedrooms: {plan.beds if plan.beds is not None else 'N/A'}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Bathrooms: {plan.baths if plan.baths is not None else 'N/A'}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Square Footage: {plan.sqft if plan.sqft else 'N/A'}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Rent Range: {rent_range}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ Security Deposit: {deposit}", styles['Normal']))
                
                # Add floor plan amenities
                plan_amenities = plan.amenities.all()
                if plan_amenities:
                    elements.append(Paragraph("&nbsp;&nbsp;◦ Amenities:", styles['Normal']))
                    for amenity in plan_amenities:
                        elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;▪ {amenity.name}", styles['Normal']))
                
                if plan.url:
                    elements.append(Paragraph(f"&nbsp;&nbsp;◦ Details URL: {plan.url}", styles['Normal']))
                
                elements.append(Spacer(1, 8))

        # Community Amenities
        community_amenities = latest_shop_info.community_amenities.all()
        if community_amenities:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Community Amenities", heading_style))
            
            for amenity in community_amenities:
                elements.append(Paragraph(f"• {amenity.name}", styles['Normal']))
                if amenity.description:
                    elements.append(Paragraph(f"&nbsp;&nbsp;◦ {amenity.description}", styles['Normal']))

        # Community Pages
        community_pages = latest_shop_info.pages.all()
        if community_pages:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Community Pages", heading_style))
            
            for page in community_pages:
                elements.append(Paragraph(f"<b>• {page.name}</b>", styles['Normal']))
                if page.overview:
                    elements.append(Paragraph(f"&nbsp;&nbsp;◦ Description: {page.overview}", styles['Normal']))
                elements.append(Paragraph(f"&nbsp;&nbsp;◦ URL: {page.url}", styles['Normal']))
                elements.append(Spacer(1, 4))

        # Additional Information
        if latest_shop_info.pet_policy or latest_shop_info.office_hours:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Additional Information", heading_style))
            
            if latest_shop_info.pet_policy:
                elements.append(Paragraph(f"<b>Pet Policy:</b> {latest_shop_info.pet_policy}", styles['Normal']))
                elements.append(Spacer(1, 6))
            
            if latest_shop_info.office_hours:
                elements.append(Paragraph(f"<b>Office Hours:</b> {latest_shop_info.office_hours}", styles['Normal']))
                elements.append(Spacer(1, 6))
            
            if latest_shop_info.self_showings is not None:
                showing_text = "Available" if latest_shop_info.self_showings else "Not available"
                elements.append(Paragraph(f"<b>Self Showings:</b> {showing_text}", styles['Normal']))

        # Build PDF
        doc.build(elements)

        # Create response
        buffer.seek(0)
        filename = f"secret_shop_report_{target.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
