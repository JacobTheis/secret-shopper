import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Target(models.Model):
    """Represents a target property for a secret shop."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Property Name"), max_length=255)
    street_address = models.CharField(_("Street Address"), max_length=255)
    city = models.CharField(_("City"), max_length=100)
    state = models.CharField(_("State"), max_length=50)
    zip_code = models.CharField(_("Zip Code"), max_length=20)
    phone_number = models.CharField(
        _("Phone Number"), max_length=20, blank=True, null=True
    )
    email_address = models.EmailField(
        _("Email Address"), max_length=254, blank=True, null=True
    )
    website = models.URLField(
        _("Website"), max_length=200, blank=True, null=True)
    owners = models.TextField(
        _("Owner(s)"),
        blank=True,
        null=True,
        help_text=_("Names or details of owners")
    )
    property_manager = models.CharField(
        _("Property Manager"), max_length=255, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Target")
        verbose_name_plural = _("Targets")
        ordering = ["name"]

    def __str__(self) -> str:
        """Return the string representation of the Target."""
        return self.name
