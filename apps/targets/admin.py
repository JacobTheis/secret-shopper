from django.contrib import admin
from .models import Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    """Admin configuration for the Target model."""

    list_display = (
        "name",
        "city",
        "state",
        "website",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "street_address", "city", "state", "zip_code")
    list_filter = ("state", "city", "created_at")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    "street_address",
                    "city",
                    "state",
                    "zip_code",
                )
            },
        ),
        (
            "Contact Information",
            {"fields": ("phone_number", "email_address", "website")},
        ),
        ("Management Details", {"fields": ("owners", "property_manager")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
