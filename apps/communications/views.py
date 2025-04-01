from django.shortcuts import render

# Create your views here.
    from django.views.generic import TemplateView
    from django.contrib.auth.mixins import LoginRequiredMixin

    class CommunicationsView(LoginRequiredMixin, TemplateView):
        """Communications main view. Requires authenticated user."""
        template_name = "communications/index.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['page_title'] = 'Communications'
            # Add any additional context needed for the template here
            return context
