"""Tests for views and URL routing."""

from django.test import Client, TestCase
from django.urls import reverse

from fl_license_scraper.accounts.models import User
from fl_license_scraper.scraper.models import License, TradeCategory


class HomeViewTests(TestCase):
    """Tests for the home page."""

    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        assert response.status_code == 200

    def test_about_page_loads(self):
        response = self.client.get(reverse("about"))
        assert response.status_code == 200


class LicenseSearchViewTests(TestCase):
    """Tests for license search views."""

    def setUp(self):
        self.client = Client()
        self.category = TradeCategory.objects.create(
            name="Electrical", slug="electrical",
        )
        self.license = License.objects.create(
            license_number="EC13055555",
            licensee_name="View Test Contractor",
            status="active",
            category=self.category,
            city="Fort Lauderdale",
            county="Broward",
        )

    def test_search_page_loads(self):
        response = self.client.get(reverse("scraper:search"))
        assert response.status_code == 200

    def test_search_by_name(self):
        response = self.client.get(reverse("scraper:search"), {"q": "View Test"})
        assert response.status_code == 200

    def test_license_detail(self):
        response = self.client.get(
            reverse("scraper:license_detail", kwargs={"license_number": "EC13055555"})
        )
        assert response.status_code == 200
        assert b"View Test Contractor" in response.content

    def test_category_list(self):
        response = self.client.get(reverse("scraper:category_list"))
        assert response.status_code == 200

    def test_category_detail(self):
        response = self.client.get(
            reverse("scraper:category_detail", kwargs={"slug": "electrical"})
        )
        assert response.status_code == 200


class LegalSearchViewTests(TestCase):
    """Tests for legal case search views."""

    def setUp(self):
        self.client = Client()

    def test_legal_search_page_loads(self):
        response = self.client.get(reverse("legal:search"))
        assert response.status_code == 200


class JobBoardViewTests(TestCase):
    """Tests for job board views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123",
        )

    def test_job_list_loads(self):
        response = self.client.get(reverse("jobs:job_list"))
        assert response.status_code == 200

    def test_contractor_list_loads(self):
        response = self.client.get(reverse("jobs:contractor_list"))
        assert response.status_code == 200

    def test_job_create_requires_login(self):
        response = self.client.get(reverse("jobs:job_create"))
        assert response.status_code == 302  # Redirect to login

    def test_job_create_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("jobs:job_create"))
        assert response.status_code == 200

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("jobs:dashboard"))
        assert response.status_code == 302


class APIViewTests(TestCase):
    """Tests for REST API endpoints."""

    def setUp(self):
        self.client = Client()
        self.license = License.objects.create(
            license_number="EC13077777",
            licensee_name="API Test",
            status="active",
        )

    def test_api_license_list(self):
        response = self.client.get("/api/licenses/")
        assert response.status_code == 200

    def test_api_license_lookup(self):
        response = self.client.get("/api/licenses/lookup/EC13077777/")
        assert response.status_code == 200

    def test_api_license_lookup_not_found(self):
        response = self.client.get("/api/licenses/lookup/FAKE999/")
        assert response.status_code == 404

    def test_api_legal_cases(self):
        response = self.client.get("/api/legal/cases/")
        assert response.status_code == 200

    def test_api_jobs(self):
        response = self.client.get("/api/jobs/postings/")
        assert response.status_code == 200

    def test_api_contractors(self):
        response = self.client.get("/api/jobs/contractors/")
        assert response.status_code == 200
