"""API URL routes for the job board."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r"postings", api_views.JobViewSet, basename="job")
router.register(r"contractors", api_views.ContractorViewSet, basename="contractor")
router.register(r"reviews", api_views.ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
