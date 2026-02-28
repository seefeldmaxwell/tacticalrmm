"""API views for legal case data."""
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import LegalCase
from .serializers import LegalCaseDetailSerializer, LegalCaseSerializer


class LegalCaseViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for browsing legal cases."""

    permission_classes = [AllowAny]
    filterset_fields = ["case_type", "status", "severity", "source"]
    search_fields = ["case_number", "title", "respondent_name", "license__licensee_name"]
    ordering_fields = ["filed_date", "fine_amount", "status"]

    def get_queryset(self):
        return LegalCase.objects.select_related("license").order_by("-filed_date")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LegalCaseDetailSerializer
        return LegalCaseSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def cases_for_license(request, license_number):
    """Get all legal cases for a specific license number."""
    cases = (
        LegalCase.objects.filter(license__license_number=license_number)
        .select_related("license")
        .order_by("-filed_date")
    )
    serializer = LegalCaseSerializer(cases, many=True)
    return Response(serializer.data)
