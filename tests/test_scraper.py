"""Tests for the Florida license scraper module."""

import pytest
from django.test import TestCase
from django.utils import timezone

from fl_license_scraper.scraper.models import License, LicenseHistory, ScrapeLog, TradeCategory
from fl_license_scraper.scraper.scraper_engine import DBPRScraper, TRADE_LICENSE_TYPES


class TradeCategoryTests(TestCase):
    """Tests for trade categories."""

    def test_create_category(self):
        cat = TradeCategory.objects.create(
            name="Electrical Contractors",
            slug="electrical",
            dbpr_code="5102",
        )
        assert cat.name == "Electrical Contractors"
        assert str(cat) == "Electrical Contractors"

    def test_category_url(self):
        cat = TradeCategory.objects.create(name="Plumbing", slug="plumbing")
        assert "/category/plumbing/" in cat.get_absolute_url()


class LicenseTests(TestCase):
    """Tests for license model."""

    def setUp(self):
        self.category = TradeCategory.objects.create(
            name="Electrical", slug="electrical", dbpr_code="5102",
        )
        self.license = License.objects.create(
            license_number="EC13012345",
            licensee_name="John Smith",
            business_name="Smith Electric LLC",
            license_type="Electrical Contractor",
            status="active",
            category=self.category,
            city="Miami",
            county="Miami-Dade",
            state="FL",
        )

    def test_license_str(self):
        assert "EC13012345" in str(self.license)
        assert "John Smith" in str(self.license)

    def test_license_is_active(self):
        assert self.license.is_active is True

    def test_license_is_not_active(self):
        self.license.status = "suspended"
        assert self.license.is_active is False

    def test_license_url(self):
        url = self.license.get_absolute_url()
        assert "EC13012345" in url

    def test_license_expired_check(self):
        from datetime import timedelta
        self.license.expiration_date = timezone.now().date() - timedelta(days=30)
        assert self.license.is_expired is True

    def test_license_not_expired(self):
        from datetime import timedelta
        self.license.expiration_date = timezone.now().date() + timedelta(days=30)
        assert self.license.is_expired is False

    def test_no_legal_cases(self):
        assert self.license.has_legal_cases is False
        assert self.license.legal_case_count == 0


class LicenseHistoryTests(TestCase):
    """Tests for license history tracking."""

    def test_create_history(self):
        license_obj = License.objects.create(
            license_number="CFC123456",
            licensee_name="Jane Doe",
            status="active",
        )
        history = LicenseHistory.objects.create(
            license=license_obj,
            field_changed="status",
            old_value="inactive",
            new_value="active",
        )
        assert "status" in str(history)


class ScrapeLogTests(TestCase):
    """Tests for scrape logging."""

    def test_create_log(self):
        log = ScrapeLog.objects.create(
            status="completed",
            total_found=100,
            new_licenses=50,
            updated_licenses=50,
        )
        assert log.status == "completed"
        assert "completed" in str(log)


class DBPRScraperTests(TestCase):
    """Tests for the scraper engine (unit tests, no HTTP calls)."""

    def setUp(self):
        self.scraper = DBPRScraper()

    def test_normalize_status_active(self):
        assert self.scraper._normalize_status("Current") == "active"
        assert self.scraper._normalize_status("current,active") == "active"
        assert self.scraper._normalize_status("Active") == "active"
        assert self.scraper._normalize_status("Clear/Active") == "active"

    def test_normalize_status_other(self):
        assert self.scraper._normalize_status("Suspended") == "suspended"
        assert self.scraper._normalize_status("Revoked") == "revoked"
        assert self.scraper._normalize_status("Expired") == "expired"
        assert self.scraper._normalize_status("Null and Void") == "null_and_void"

    def test_normalize_status_unknown(self):
        assert self.scraper._normalize_status("") == "unknown"
        assert self.scraper._normalize_status("Something Weird") == "unknown"

    def test_parse_date_valid(self):
        result = self.scraper._parse_date("01/15/2024")
        assert result is not None
        assert result.month == 1
        assert result.day == 15
        assert result.year == 2024

    def test_parse_date_invalid(self):
        assert self.scraper._parse_date("") is None
        assert self.scraper._parse_date("N/A") is None
        assert self.scraper._parse_date("not a date") is None

    def test_determine_category_by_prefix(self):
        cat = self.scraper._determine_category("", "EC13012345")
        assert cat is not None
        assert cat.slug == "electrical"

    def test_determine_category_plumbing(self):
        cat = self.scraper._determine_category("", "CFC123456")
        assert cat is not None
        assert cat.slug == "plumbing"

    def test_determine_category_hvac(self):
        cat = self.scraper._determine_category("", "CAC054321")
        assert cat is not None
        assert cat.slug == "hvac"

    def test_save_license(self):
        data = {
            "license_number": "EC99999999",
            "licensee_name": "Test Electrician",
            "business_name": "Test Electric Inc",
            "license_type": "Electrical Contractor",
            "status": "Current",
            "city": "Tampa",
            "county": "Hillsborough",
            "state": "FL",
        }
        license_obj = self.scraper.save_license(data)
        assert license_obj is not None
        assert license_obj.license_number == "EC99999999"
        assert license_obj.status == "active"
        assert license_obj.city == "Tampa"

    def test_save_license_empty(self):
        result = self.scraper.save_license({})
        assert result is None

    def test_trade_license_types_complete(self):
        """Ensure all expected trades are configured."""
        expected = ["electrical", "plumbing", "hvac", "general_contractor", "roofing"]
        for trade in expected:
            assert trade in TRADE_LICENSE_TYPES
