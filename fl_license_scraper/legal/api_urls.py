"""API URL routes for legal cases."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r"cases", api_views.LegalCaseViewSet, basename="legal-case")

urlpatterns = [
    path(
        "lookup/<str:license_number>/",
        api_views.cases_for_license,
        name="api-legal-lookup",
    ),
    path("", include(router.urls)),
]
