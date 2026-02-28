"""Views for legal case search and display."""

from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import LegalCase


@require_GET
def case_search(request):
    """Search for legal cases against Florida licenses."""
    query = request.GET.get("q", "").strip()
    license_number = request.GET.get("license_number", "").strip()
    case_type = request.GET.get("case_type", "").strip()
    status_filter = request.GET.get("status", "").strip()

    cases = LegalCase.objects.select_related("license", "license__category")
    results = None
    searched = False

    if query or license_number or case_type or status_filter:
        searched = True

        if license_number:
            cases = cases.filter(license__license_number__icontains=license_number)
        if query:
            cases = cases.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(case_number__icontains=query)
                | Q(respondent_name__icontains=query)
                | Q(license__licensee_name__icontains=query)
            )
        if case_type:
            cases = cases.filter(case_type=case_type)
        if status_filter:
            cases = cases.filter(status=status_filter)

        results = cases.order_by("-filed_date")[:100]

    # Stats
    total_cases = LegalCase.objects.count()
    open_cases = LegalCase.objects.filter(status="open").count()
    total_fines = LegalCase.objects.aggregate(total=Sum("fine_amount"))["total"] or 0

    context = {
        "results": results,
        "searched": searched,
        "query": query,
        "license_number": license_number,
        "case_type": case_type,
        "status_filter": status_filter,
        "case_type_choices": LegalCase.CASE_TYPE_CHOICES,
        "status_choices": LegalCase.STATUS_CHOICES,
        "total_cases": total_cases,
        "open_cases": open_cases,
        "total_fines": total_fines,
    }
    return render(request, "legal/search.html", context)


def case_detail(request, case_number):
    """Detailed view of a legal case."""
    case = get_object_or_404(
        LegalCase.objects.select_related("license", "license__category"),
        case_number=case_number,
    )
    documents = case.documents.all()
    notes = case.notes.order_by("-created_at")

    # Other cases for the same license
    related_cases = (
        LegalCase.objects.filter(license=case.license)
        .exclude(pk=case.pk)
        .order_by("-filed_date")[:10]
    )

    context = {
        "case": case,
        "documents": documents,
        "notes": notes,
        "related_cases": related_cases,
    }
    return render(request, "legal/case_detail.html", context)


def license_cases(request, license_number):
    """View all legal cases for a specific license number."""
    cases = (
        LegalCase.objects.filter(license__license_number=license_number)
        .select_related("license")
        .order_by("-filed_date")
    )
    total_fines = cases.aggregate(total=Sum("fine_amount"))["total"] or 0

    context = {
        "cases": cases,
        "license_number": license_number,
        "total_fines": total_fines,
    }
    return render(request, "legal/license_cases.html", context)
