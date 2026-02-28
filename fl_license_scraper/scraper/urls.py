"""URL routes for the license scraper."""
from django.urls import path
from . import views

app_name = "scraper"

urlpatterns = [
    path("", views.license_search, name="search"),
    path("categories/", views.category_list, name="category_list"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("<str:license_number>/", views.license_detail, name="license_detail"),
]
