from django.contrib import admin

from .models import Shop, ShopResult


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Admin configuration for the Shop model."""

    list_display = (
        "id",
        "user",
        "persona",
        "target",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "user", "created_at")
    search_fields = ("target__name", "user__username", "persona__name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25


@admin.register(ShopResult)
class ShopResultAdmin(admin.ModelAdmin):
    """Admin configuration for the ShopResult model."""

    list_display = ("shop", "created_at", "updated_at")
    search_fields = (
        "shop__target__name",
        "shop__user__username",
        "shop__persona__name",
    )
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
