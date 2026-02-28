"""URL configuration for Florida License Scraper & Job Board."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Main pages
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    # App URLs
    path("licenses/", include("fl_license_scraper.scraper.urls")),
    path("legal/", include("fl_license_scraper.legal.urls")),
    path("jobs/", include("fl_license_scraper.jobs.urls")),
    path("accounts/", include("fl_license_scraper.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    # API
    path("api/licenses/", include("fl_license_scraper.scraper.api_urls")),
    path("api/legal/", include("fl_license_scraper.legal.api_urls")),
    path("api/jobs/", include("fl_license_scraper.jobs.api_urls")),
    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
