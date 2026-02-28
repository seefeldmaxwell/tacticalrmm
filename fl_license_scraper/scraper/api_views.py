"""API views for license data."""
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import License, TradeCategory
from .scraper_engine import lookup_license
from .serializers import LicenseDetailSerializer, LicenseSerializer, TradeCategorySerializer


class LicenseViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for browsing licenses."""

    permission_classes = [AllowAny]
    filterset_fields = ["status", "category__slug", "county", "city"]
    search_fields = ["licensee_name", "business_name", "license_number"]
    ordering_fields = ["licensee_name", "last_scraped", "status"]

    def get_queryset(self):
        return License.objects.select_related("category").order_by("-last_scraped")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LicenseDetailSerializer
        return LicenseSerializer


class TradeCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for trade categories."""

    permission_classes = [AllowAny]
    serializer_class = TradeCategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        return TradeCategory.objects.annotate(
            license_count=Count("licenses")
        ).order_by("name")


@api_view(["GET"])
@permission_classes([AllowAny])
def license_lookup(request, license_number):
    """
    Look up a Florida license by number.

    Checks the local database first, then scrapes DBPR if not found
    or if data is stale (older than 24 hours).
    """
    license_obj = lookup_license(license_number)
    if license_obj:
        serializer = LicenseDetailSerializer(license_obj)
        return Response(serializer.data)
    return Response(
        {"error": f"License {license_number} not found"},
        status=status.HTTP_404_NOT_FOUND,
    )
