"""Admin configuration for job board models."""
from django.contrib import admin
from .models import Bid, ContractorPortfolioItem, ContractorProfile, Job, Message, Review


class PortfolioInline(admin.TabularInline):
    model = ContractorPortfolioItem
    extra = 0


@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "company_name", "user", "city", "county",
        "is_verified", "avg_rating", "total_reviews", "membership_level",
    ]
    list_filter = ["is_verified", "is_featured", "membership_level", "county"]
    search_fields = ["company_name", "user__username", "user__email"]
    raw_id_fields = ["user", "license"]
    inlines = [PortfolioInline]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "title", "posted_by", "category", "status",
        "city", "urgency", "budget_range", "bids_count", "created_at",
    ]
    list_filter = ["status", "category", "urgency", "county"]
    search_fields = ["title", "description"]
    raw_id_fields = ["posted_by", "assigned_contractor"]
    date_hierarchy = "created_at"


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ["job", "contractor", "amount", "status", "created_at"]
    list_filter = ["status"]
    raw_id_fields = ["job", "contractor"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "contractor", "reviewer", "overall_rating", "rating",
        "would_hire_again", "is_verified", "created_at",
    ]
    list_filter = ["overall_rating", "is_verified", "would_hire_again"]
    search_fields = ["title", "comment", "contractor__company_name"]
    raw_id_fields = ["contractor", "reviewer", "job"]
