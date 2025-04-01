from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class PersonasView(LoginRequiredMixin, TemplateView):
    """Personas main view. Requires authenticated user."""
    template_name = "personas/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Personas'
        # Add any additional context needed for the template here
        return context
