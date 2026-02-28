"""Template context processors."""

from fl_license_scraper.scraper.models import TradeCategory


def site_context(request):
    """Add site-wide context variables."""
    return {
        "site_name": "FL License Lookup",
        "site_tagline": "Florida Skilled Trade License Search & Job Board",
        "nav_categories": TradeCategory.objects.order_by("name")[:10],
    }
