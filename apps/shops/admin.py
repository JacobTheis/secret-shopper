from django.contrib import admin
from django.urls import reverse # Import reverse
from django.utils.html import format_html

from .models import (Amenity, CommunityInfo, CommunityPage, FloorPlan, Shop,
                     ShopResult)


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
    readonly_fields = ("created_at", "updated_at", "shop") # Make shop read-only here too
    list_per_page = 25

    @admin.display(description="Community Info")
    def get_community_info_link(self, obj):
        """Provide a link to the related CommunityInfo admin page."""
        # Ensure reverse is imported at the top: from django.urls import reverse
        try:
            info = obj.community_info
            if info:
                url = reverse(
                    "admin:shops_communityinfo_change", args=[info.pk]
                )
                return format_html('<a href="{}">View/Edit Details</a>', url)
        except CommunityInfo.DoesNotExist:
            pass
        return "No Community Info"

# Optional: Register FloorPlan directly if needed for separate management/filtering
# @admin.register(FloorPlan)
# class FloorPlanAdmin(admin.ModelAdmin):
#     list_display = ('name', 'community_info', 'beds', 'baths', 'sqft', 'min_rental_price', 'max_rental_price')
#     list_filter = ('beds', 'baths', 'type', 'community_info')
#     search_fields = ('name', 'type', 'community_info__name')
#     filter_horizontal = ('amenities',)
#     readonly_fields = ('created_at', 'updated_at')
#     list_per_page = 50


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """Admin configuration for the Amenity model."""

    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50


class CommunityPageInline(admin.TabularInline):
    """Inline admin for Community Pages within CommunityInfo."""

    model = CommunityPage
    extra = 0  # Don't show extra blank forms by default
    fields = ("name", "overview", "url")
    readonly_fields = ("created_at", "updated_at")


class FloorPlanInline(admin.TabularInline):
    """Inline admin for Floor Plans within CommunityInfo."""

    model = FloorPlan
    extra = 0
    fields = (
        "name",
        "beds",
        "baths",
        "sqft",
        "type",
        "min_rental_price",
        "max_rental_price",
        "security_deposit",
        "url",
    )
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("amenities",) # Use filter_horizontal for ManyToMany


@admin.register(CommunityInfo)
class CommunityInfoAdmin(admin.ModelAdmin):
    """Admin configuration for the CommunityInfo model."""

    list_display = (
        "name",
        "get_shop_target",
        "url",
        "application_fee",
        "administration_fee",
        "membership_fee",
        "created_at",
    )
    list_filter = ("created_at", "self_showings")
    search_fields = (
        "name",
        "overview",
        "url",
        "shop_result__shop__target__name",
        "shop_result__shop__user__username",
    )
    readonly_fields = ("created_at", "updated_at", "shop_result") # shop_result is set programmatically
    filter_horizontal = ("community_amenities",)
    inlines = [CommunityPageInline, FloorPlanInline]
    list_per_page = 25

    fieldsets = (
        (
            "Core Info",
            {
                "fields": (
                    "shop_result",
                    "name",
                    "overview",
                    "url",
                    "office_hours",
                    "resident_portal_provider",
                )
            },
        ),
        (
            "Fees & Policies",
            {
                "fields": (
                    "application_fee",
                    "application_fee_source",
                    "administration_fee",
                    "administration_fee_source",
                    "membership_fee",
                    "membership_fee_source",
                    "pet_policy",
                    "pet_policy_source",
                )
            },
        ),
        (
            "Features",
            {"fields": ("self_showings", "self_showings_source", "community_amenities")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Target", ordering="shop_result__shop__target__name")
    def get_shop_target(self, obj):
        """Display the target name from the related Shop."""
        if obj.shop_result and obj.shop_result.shop:
            return obj.shop_result.shop.target
        return "N/A"


@admin.register(ShopResult)
class ShopResultAdmin(admin.ModelAdmin):
    """Admin configuration for the ShopResult model (now primarily a link)."""

    list_display = ("shop", "get_community_info_link", "created_at", "updated_at")
    search_fields = (
        "shop__target__name",
        "shop__user__username",
    )
    readonly_fields = ("created_at", "updated_at", "shop")
    list_per_page = 25

    @admin.display(description="Community Info")
    def get_community_info_link(self, obj):
        """Provide a link to the related CommunityInfo admin page."""
        try:
            info = obj.community_info
            if info:
                url = reverse(
                    "admin:shops_communityinfo_change", args=[info.pk]
                ) # Requires: from django.urls import reverse
                return format_html('<a href="{}">View/Edit Details</a>', url)
        except CommunityInfo.DoesNotExist:
            pass
        return "No Community Info"

# Optional: Register FloorPlan directly if needed for separate management/filtering
# @admin.register(FloorPlan)
# class FloorPlanAdmin(admin.ModelAdmin):
#     list_display = ('name', 'community_info', 'beds', 'baths', 'sqft', 'min_rental_price', 'max_rental_price')
#     list_filter = ('beds', 'baths', 'type', 'community_info')
#     search_fields = ('name', 'type', 'community_info__name')
#     filter_horizontal = ('amenities',)
#     readonly_fields = ('created_at', 'updated_at')
#     list_per_page = 50
