"""Main views for the Florida License Scraper & Job Board."""

from django.db.models import Avg, Count
from django.shortcuts import render

from fl_license_scraper.jobs.models import Job, ContractorProfile
from fl_license_scraper.scraper.models import License, TradeCategory


def home(request):
    """Landing page with search, featured contractors, and recent jobs."""
    trade_categories = TradeCategory.objects.annotate(
        license_count=Count("licenses")
    ).order_by("-license_count")[:12]

    featured_contractors = (
        ContractorProfile.objects.filter(is_verified=True, is_featured=True)
        .select_related("user", "license")
        .annotate(avg_rating=Avg("reviews__rating"))
        .order_by("-avg_rating")[:6]
    )

    recent_jobs = (
        Job.objects.filter(status="open")
        .select_related("posted_by", "category")
        .order_by("-created_at")[:8]
    )

    recent_licenses = (
        License.objects.filter(status="active")
        .select_related("category")
        .order_by("-last_scraped")[:10]
    )

    context = {
        "trade_categories": trade_categories,
        "featured_contractors": featured_contractors,
        "recent_jobs": recent_jobs,
        "recent_licenses": recent_licenses,
    }
    return render(request, "base/home.html", context)


def about(request):
    """About page."""
    stats = {
        "total_licenses": License.objects.count(),
        "active_licenses": License.objects.filter(status="active").count(),
        "total_contractors": ContractorProfile.objects.filter(is_verified=True).count(),
        "total_jobs": Job.objects.filter(status="open").count(),
        "trade_categories": TradeCategory.objects.count(),
    }
    return render(request, "base/about.html", {"stats": stats})
