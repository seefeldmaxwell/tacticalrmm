"""Tests for the job board module."""

from decimal import Decimal

from django.test import TestCase

from fl_license_scraper.accounts.models import User
from fl_license_scraper.jobs.models import (
    Bid,
    ContractorProfile,
    Job,
    Review,
)
from fl_license_scraper.scraper.models import License, TradeCategory


class ContractorProfileTests(TestCase):
    """Tests for contractor profiles."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="contractor1",
            password="testpass123",
            role="contractor",
        )
        self.license = License.objects.create(
            license_number="EC13000001",
            licensee_name="Test Contractor",
            status="active",
        )
        self.contractor = ContractorProfile.objects.create(
            user=self.user,
            license=self.license,
            company_name="Test Electric Co",
            city="Miami",
            county="Miami-Dade",
            is_verified=True,
        )

    def test_contractor_str(self):
        assert str(self.contractor) == "Test Electric Co"

    def test_contractor_url(self):
        url = self.contractor.get_absolute_url()
        assert str(self.contractor.pk) in url


class JobTests(TestCase):
    """Tests for job postings."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="homeowner1",
            password="testpass123",
            role="homeowner",
        )
        self.category = TradeCategory.objects.create(
            name="Electrical", slug="electrical",
        )
        self.job = Job.objects.create(
            title="Fix kitchen outlet",
            description="Outlet sparking, needs replacement",
            category=self.category,
            posted_by=self.user,
            city="Tampa",
            county="Hillsborough",
            urgency="within_week",
            budget_range="under_500",
        )

    def test_job_str(self):
        assert str(self.job) == "Fix kitchen outlet"

    def test_job_url(self):
        url = self.job.get_absolute_url()
        assert str(self.job.pk) in url

    def test_job_default_status(self):
        assert self.job.status == "open"


class BidTests(TestCase):
    """Tests for bids."""

    def setUp(self):
        self.homeowner = User.objects.create_user(
            username="homeowner2", password="testpass123",
        )
        self.contractor_user = User.objects.create_user(
            username="contractor2", password="testpass123", role="contractor",
        )
        self.contractor = ContractorProfile.objects.create(
            user=self.contractor_user,
            company_name="Pro Electric",
            city="Orlando",
            is_verified=True,
        )
        self.job = Job.objects.create(
            title="Panel upgrade",
            description="200 amp panel upgrade needed",
            posted_by=self.homeowner,
            city="Orlando",
        )
        self.bid = Bid.objects.create(
            job=self.job,
            contractor=self.contractor,
            amount=Decimal("2500.00"),
            description="Full panel upgrade with permit",
            estimated_duration="2 days",
        )

    def test_bid_str(self):
        assert "$2500" in str(self.bid)
        assert "Pro Electric" in str(self.bid)

    def test_bid_default_status(self):
        assert self.bid.status == "pending"


class ReviewTests(TestCase):
    """Tests for reviews."""

    def setUp(self):
        self.reviewer = User.objects.create_user(
            username="reviewer1", password="testpass123",
        )
        self.contractor_user = User.objects.create_user(
            username="contractor3", password="testpass123", role="contractor",
        )
        self.contractor = ContractorProfile.objects.create(
            user=self.contractor_user,
            company_name="Great Plumbing",
            city="Jacksonville",
            is_verified=True,
        )

    def test_create_review(self):
        review = Review.objects.create(
            contractor=self.contractor,
            reviewer=self.reviewer,
            title="Great work!",
            comment="They did an excellent job fixing our pipes.",
            overall_rating=5,
            quality_rating=5,
            price_rating=4,
            punctuality_rating=5,
            professionalism_rating=5,
            responsiveness_rating=5,
            would_hire_again=True,
        )
        assert review.rating > 0
        assert review.letter_grade == "A"

    def test_review_updates_contractor_rating(self):
        Review.objects.create(
            contractor=self.contractor,
            reviewer=self.reviewer,
            title="Good",
            comment="Good service",
            overall_rating=4,
        )
        self.contractor.refresh_from_db()
        assert self.contractor.total_reviews == 1
        assert self.contractor.avg_rating > 0

    def test_letter_grades(self):
        review = Review(overall_rating=5, quality_rating=5, price_rating=5,
                       punctuality_rating=5, professionalism_rating=5,
                       responsiveness_rating=5)
        review.rating = 5.0
        assert review.letter_grade == "A"

        review.rating = 3.5
        assert review.letter_grade == "B"

        review.rating = 2.5
        assert review.letter_grade == "C"

        review.rating = 1.5
        assert review.letter_grade == "D"

        review.rating = 1.0
        assert review.letter_grade == "F"
