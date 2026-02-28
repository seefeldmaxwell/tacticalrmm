"""API views for the job board."""
from rest_framework import permissions, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import ContractorProfile, Job, Review
from .serializers import ContractorSerializer, JobSerializer, ReviewSerializer


class JobViewSet(viewsets.ModelViewSet):
    """API endpoint for job postings."""

    filterset_fields = ["status", "category__slug", "county", "city", "urgency", "budget_range"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "urgency"]

    def get_queryset(self):
        return Job.objects.select_related("posted_by", "category").order_by("-created_at")

    def get_serializer_class(self):
        return JobSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class ContractorViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for contractor profiles."""

    permission_classes = [AllowAny]
    serializer_class = ContractorSerializer
    filterset_fields = ["city", "county", "is_verified", "membership_level"]
    search_fields = ["company_name", "description"]
    ordering_fields = ["avg_rating", "total_reviews", "years_experience"]

    def get_queryset(self):
        return ContractorProfile.objects.filter(
            is_verified=True
        ).select_related("user", "license").order_by("-avg_rating")


class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for contractor reviews."""

    serializer_class = ReviewSerializer
    filterset_fields = ["contractor", "overall_rating"]
    ordering_fields = ["created_at", "rating"]

    def get_queryset(self):
        return Review.objects.select_related("reviewer", "contractor").order_by("-created_at")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
