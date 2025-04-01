from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Persona(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='personas'
    )
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    rental_budget = models.DecimalField(
        _("Rental Budget"),
        max_digits=10,
        decimal_places=2
    )
    desired_bedrooms = models.PositiveIntegerField(_("Desired Bedrooms"))
    desired_bathrooms = models.PositiveIntegerField(_("Desired Bathrooms"))
    additional_preferences = models.TextField(
        _("Additional Rental Preferences"),
        blank=True
    )
    pets = models.TextField(_("Pets"), blank=True)
    credit_score = models.PositiveIntegerField(_("Credit Score"))
    monthly_income = models.PositiveIntegerField(_("Monthly Income"))
    additional_occupants = models.TextField(
        _("Additional Occupants"),
        blank=True
    )
    rental_history = models.TextField(_("Rental History"), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Persona Template")
        verbose_name_plural = _("Persona Templates")
        ordering = ['-created']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
