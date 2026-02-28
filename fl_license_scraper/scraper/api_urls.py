"""API URL routes for the license scraper."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r"", api_views.LicenseViewSet, basename="license")
router.register(r"categories", api_views.TradeCategoryViewSet, basename="category")

urlpatterns = [
    path("lookup/<str:license_number>/", api_views.license_lookup, name="api-license-lookup"),
    path("", include(router.urls)),
]
