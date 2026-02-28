"""Admin configuration for license models."""
from django.contrib import admin
from .models import License, LicenseHistory, ScrapeLog, TradeCategory


@admin.register(TradeCategory)
class TradeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "dbpr_code"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class LicenseHistoryInline(admin.TabularInline):
    model = LicenseHistory
    extra = 0
    readonly_fields = ["field_changed", "old_value", "new_value", "changed_at"]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = [
        "license_number", "licensee_name", "license_type",
        "status", "city", "county", "last_scraped",
    ]
    list_filter = ["status", "category", "county"]
    search_fields = ["license_number", "licensee_name", "business_name"]
    readonly_fields = ["last_scraped", "created_at", "updated_at"]
    inlines = [LicenseHistoryInline]
    date_hierarchy = "last_scraped"


@admin.register(ScrapeLog)
class ScrapeLogAdmin(admin.ModelAdmin):
    list_display = [
        "started_at", "status", "category", "total_found",
        "new_licenses", "updated_licenses", "errors",
    ]
    list_filter = ["status", "category"]
    readonly_fields = [
        "started_at", "completed_at", "total_found",
        "new_licenses", "updated_licenses", "errors",
    ]
