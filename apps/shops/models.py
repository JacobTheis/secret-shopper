from django.conf import settings
from django.db import models

from apps.personas.models import Persona
from apps.targets.models import Target


class Shop(models.Model):
    """Represents a single secret shopping interaction instance."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        ERROR = "ERROR", "Error"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shops",
        help_text="The user who initiated the shop.",
    )
    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,  # Prevent deleting Persona if used in a Shop
        related_name="shops",
        help_text="The persona used for this shop.",
    )
    target = models.ForeignKey(
        Target,
        on_delete=models.CASCADE,
        related_name="shops",
        help_text="The target being shopped.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="The current status of the shop.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self) -> str:
        """String representation of the Shop model."""
        return f"Shop for {self.target} by {self.user} ({self.get_status_display()})"


class ShopResult(models.Model):
    """Stores the summarized results and extracted data for a completed shop."""

    shop = models.OneToOneField(
        Shop,
        on_delete=models.CASCADE,
        related_name="result",
        primary_key=True,
        help_text="The shop this result belongs to.",
    )
    summary = models.TextField(
        blank=True, help_text="AI-generated summary of the interaction."
    )
    extracted_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured data extracted from the interaction.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shop Result"
        verbose_name_plural = "Shop Results"

    def __str__(self) -> str:
        """String representation of the ShopResult model."""
        return f"Result for {self.shop}"
