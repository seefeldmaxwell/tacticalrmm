"""Views for license search and display."""

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from .models import License, ScrapeLog, TradeCategory
from .scraper_engine import lookup_license


@require_GET
def license_search(request):
    """Main license search page."""
    query = request.GET.get("q", "").strip()
    license_number = request.GET.get("license_number", "").strip()
    county = request.GET.get("county", "").strip()
    trade = request.GET.get("trade", "").strip()
    status_filter = request.GET.get("status", "").strip()

    licenses = License.objects.select_related("category")
    results = None
    searched = False

    if license_number:
        searched = True
        # Direct license number lookup - try scraping if not found
        license_obj = lookup_license(license_number)
        if license_obj:
            return redirect("scraper:license_detail", license_number=license_obj.license_number)
        else:
            messages.warning(request, f"No license found with number: {license_number}")
            results = License.objects.none()

    elif query or county or trade or status_filter:
        searched = True
        if query:
            licenses = licenses.filter(
                Q(licensee_name__icontains=query)
                | Q(business_name__icontains=query)
                | Q(dba_name__icontains=query)
                | Q(license_number__icontains=query)
            )
        if county:
            licenses = licenses.filter(county__iexact=county)
        if trade:
            licenses = licenses.filter(category__slug=trade)
        if status_filter:
            licenses = licenses.filter(status=status_filter)

        results = licenses.order_by("-last_scraped")[:100]

    categories = TradeCategory.objects.annotate(
        license_count=Count("licenses")
    ).order_by("name")

    counties = (
        License.objects.exclude(county="")
        .values_list("county", flat=True)
        .distinct()
        .order_by("county")
    )

    context = {
        "results": results,
        "searched": searched,
        "query": query,
        "license_number": license_number,
        "county": county,
        "trade": trade,
        "status_filter": status_filter,
        "categories": categories,
        "counties": counties,
        "status_choices": License.STATUS_CHOICES,
    }
    return render(request, "scraper/search.html", context)


def license_detail(request, license_number):
    """Detailed view of a single license."""
    license_obj = get_object_or_404(License, license_number=license_number)
    history = license_obj.history.order_by("-changed_at")[:20]
    legal_cases = license_obj.legal_cases.order_by("-filed_date")

    context = {
        "license": license_obj,
        "history": history,
        "legal_cases": legal_cases,
    }
    return render(request, "scraper/license_detail.html", context)


def category_detail(request, slug):
    """View all licenses in a trade category."""
    category = get_object_or_404(TradeCategory, slug=slug)
    status_filter = request.GET.get("status", "")
    county = request.GET.get("county", "")

    licenses = category.licenses.all()
    if status_filter:
        licenses = licenses.filter(status=status_filter)
    if county:
        licenses = licenses.filter(county__iexact=county)

    licenses = licenses.order_by("licensee_name")[:200]

    context = {
        "category": category,
        "licenses": licenses,
        "status_filter": status_filter,
        "county": county,
        "status_choices": License.STATUS_CHOICES,
    }
    return render(request, "scraper/category_detail.html", context)


def category_list(request):
    """List all trade categories."""
    categories = TradeCategory.objects.annotate(
        license_count=Count("licenses"),
        active_count=Count("licenses", filter=Q(licenses__status="active")),
    ).order_by("name")

    context = {"categories": categories}
    return render(request, "scraper/category_list.html", context)
