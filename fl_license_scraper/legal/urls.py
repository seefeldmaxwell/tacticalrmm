"""URL routes for legal cases."""
from django.urls import path
from . import views

app_name = "legal"

urlpatterns = [
    path("", views.case_search, name="search"),
    path("license/<str:license_number>/", views.license_cases, name="license_cases"),
    path("case/<str:case_number>/", views.case_detail, name="case_detail"),
]
