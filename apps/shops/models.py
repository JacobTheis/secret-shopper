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
        null=True,
        blank=True,
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
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the shop process was started."
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the shop process was completed or failed."
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
    """Links a Shop to its detailed, structured results."""

    shop = models.OneToOneField(
        Shop,
        on_delete=models.CASCADE,
        related_name="result",
        primary_key=True,
        help_text="The shop this result belongs to.",
    )
    # Raw JSON can be stored here as a backup if needed in the future
    # raw_data = models.JSONField(null=True, blank=True, help_text="Raw AI output.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shop Result Link"
        verbose_name_plural = "Shop Result Links"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """String representation of the ShopResult model."""
        return f"Result Link for {self.shop}"


class Amenity(models.Model):
    """Represents a distinct community or floor plan amenity."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The unique name of the amenity (e.g., 'Swimming Pool', 'In-unit Washer/Dryer').",
    )
    description = models.TextField(
        blank=True, help_text="Optional description of the amenity."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"

    def __str__(self) -> str:
        """String representation of the Amenity model."""
        return self.name


class CommunityInfo(models.Model):
    """Stores the structured information gathered about a community."""

    shop_result = models.OneToOneField(
        ShopResult,
        on_delete=models.CASCADE,
        related_name="community_info",
        help_text="The shop result this community information belongs to.",
    )
    name = models.CharField(
        max_length=255, blank=True, help_text="The name of the community."
    )
    overview = models.TextField(
        blank=True, help_text="A brief summary or description of the community."
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The link to the community's homepage or relevant page.",
    )
    application_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The fee charged for applying.",
    )
    application_fee_source = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The source URL for the application fee.",
    )
    administration_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The one-time administrative fee.",
    )
    administration_fee_source = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The source URL for the administration fee.",
    )
    membership_fee = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Recurring membership or resident benefit package fee.",
    )
    membership_fee_source = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The source URL for the membership fee.",
    )
    pet_policy = models.TextField(
        blank=True, help_text="The community's policy and fees on pets."
    )
    pet_policy_source = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The source URL for the pet policy.",
    )
    self_showings = models.BooleanField(
        null=True, blank=True, help_text="Whether the community offers self-showings."
    )
    self_showings_source = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The source URL for self-showing information.",
    )
    office_hours = models.CharField(
        max_length=255, blank=True, help_text="The office hours of the community."
    )
    resident_portal_provider = models.CharField(
        max_length=255,
        blank=True,
        help_text="The software provider for the resident portal.",
    )
    community_amenities = models.ManyToManyField(
        Amenity,
        related_name="communities",
        blank=True,
        help_text="Amenities available in the community.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Community Information"
        verbose_name_plural = "Community Information"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """String representation of the CommunityInfo model."""
        return f"Info for {self.name or f'ShopResult {self.shop_result_id}'}"


class CommunityPage(models.Model):
    """Represents a specific page found on the community website."""

    community_info = models.ForeignKey(
        CommunityInfo,
        on_delete=models.CASCADE,
        related_name="pages",
        help_text="The community this page belongs to.",
    )
    name = models.CharField(
        max_length=255, help_text="The name or title of the page.")
    overview = models.TextField(
        blank=True, help_text="A brief overview or description of the page."
    )
    url = models.URLField(max_length=500, help_text="The URL for the page.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Community Page"
        verbose_name_plural = "Community Pages"
        ordering = ["name"]

    def __str__(self) -> str:
        """String representation of the CommunityPage model."""
        return f"Page '{self.name}' for {self.community_info}"


class FloorPlan(models.Model):
    """Represents a specific floor plan available in the community."""

    community_info = models.ForeignKey(
        CommunityInfo,
        on_delete=models.CASCADE,
        related_name="floor_plans",
        help_text="The community this floor plan belongs to.",
    )
    name = models.CharField(
        max_length=255, help_text="The name of the floor plan.")
    beds = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Number of bedrooms."
    )
    baths = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Number of bathrooms (e.g., 1.0, 1.5, 2.0).",
    )
    url = models.URLField(
        max_length=500, blank=True, null=True, help_text="The URL for the floor plan."
    )
    sqft = models.PositiveIntegerField(
        null=True, blank=True, help_text="Square footage."
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of unit (e.g., Apartment, Townhome, Studio).",
    )
    min_rental_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum rental price.",
    )
    max_rental_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum rental price.",
    )
    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Security deposit amount.",
    )
    amenities = models.ManyToManyField(
        Amenity,
        related_name="floor_plans",
        blank=True,
        help_text="Amenities specific to this floor plan.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Floor Plan"
        verbose_name_plural = "Floor Plans"
        ordering = ["name"]

    def __str__(self) -> str:
        """String representation of the FloorPlan model."""
        return f"{self.name} ({self.beds}bd/{self.baths}ba) for {self.community_info}"
