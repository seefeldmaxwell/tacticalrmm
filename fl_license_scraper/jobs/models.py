"""
Job Board Models - Angie's List style marketplace.

Connects homeowners with licensed Florida contractors.
Includes contractor profiles, job postings, bids, reviews, and messaging.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from fl_license_scraper.scraper.models import License, TradeCategory


class ContractorProfile(models.Model):
    """
    Contractor profile linked to a verified Florida license.
    Similar to an Angie's List pro profile.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contractor_profile",
    )
    license = models.ForeignKey(
        License,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contractor_profiles",
    )

    # Business info
    company_name = models.CharField(max_length=300)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="contractor_logos/", blank=True)
    cover_photo = models.ImageField(upload_to="contractor_covers/", blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Location
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=2, default="FL")
    zip_code = models.CharField(max_length=10, blank=True)
    county = models.CharField(max_length=100, blank=True, db_index=True)
    service_radius_miles = models.IntegerField(default=25)

    # Trade info
    specialties = models.ManyToManyField(TradeCategory, blank=True, related_name="contractors")
    years_experience = models.IntegerField(default=0)
    employees_count = models.CharField(max_length=50, blank=True)
    insurance_verified = models.BooleanField(default=False)
    bonded = models.BooleanField(default=False)

    # Platform status
    is_verified = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False)
    is_accepting_jobs = models.BooleanField(default=True)
    membership_level = models.CharField(
        max_length=20,
        choices=[
            ("free", "Free"),
            ("basic", "Basic"),
            ("premium", "Premium"),
            ("elite", "Elite"),
        ],
        default="free",
    )

    # Aggregates (cached)
    avg_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    total_reviews = models.IntegerField(default=0)
    jobs_completed = models.IntegerField(default=0)
    response_time_hours = models.IntegerField(
        default=0,
        help_text="Average response time in hours",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-avg_rating", "-total_reviews"]
        indexes = [
            models.Index(fields=["city", "county"]),
            models.Index(fields=["is_verified", "is_featured"]),
        ]

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("jobs:contractor_detail", kwargs={"pk": self.pk})

    def update_rating_cache(self):
        """Recalculate cached rating and review count."""
        from django.db.models import Avg, Count
        agg = self.reviews.aggregate(avg=Avg("rating"), count=Count("id"))
        self.avg_rating = agg["avg"] or 0
        self.total_reviews = agg["count"] or 0
        self.save(update_fields=["avg_rating", "total_reviews"])


class ContractorPortfolioItem(models.Model):
    """Photos and descriptions of past work."""

    contractor = models.ForeignKey(
        ContractorProfile, on_delete=models.CASCADE, related_name="portfolio",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="portfolio/%Y/%m/")
    category = models.ForeignKey(
        TradeCategory, on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.contractor.company_name}"


class Job(models.Model):
    """A job posting by a homeowner looking for a contractor."""

    STATUS_CHOICES = [
        ("open", "Open for Bids"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    URGENCY_CHOICES = [
        ("flexible", "Flexible Timeline"),
        ("within_month", "Within a Month"),
        ("within_week", "Within a Week"),
        ("urgent", "Urgent / Emergency"),
    ]

    BUDGET_CHOICES = [
        ("under_500", "Under $500"),
        ("500_1000", "$500 - $1,000"),
        ("1000_5000", "$1,000 - $5,000"),
        ("5000_10000", "$5,000 - $10,000"),
        ("10000_25000", "$10,000 - $25,000"),
        ("25000_50000", "$25,000 - $50,000"),
        ("over_50000", "Over $50,000"),
        ("not_sure", "Not Sure"),
    ]

    # Core
    title = models.CharField(max_length=300)
    description = models.TextField()
    category = models.ForeignKey(
        TradeCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="jobs",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", db_index=True)

    # Posted by
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_jobs",
    )

    # Location
    city = models.CharField(max_length=100, db_index=True)
    county = models.CharField(max_length=100, blank=True, db_index=True)
    zip_code = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=300, blank=True)

    # Job details
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default="flexible")
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES, default="not_sure")
    preferred_start_date = models.DateField(null=True, blank=True)
    requires_license = models.BooleanField(
        default=True,
        help_text="Require contractor to have active FL license",
    )

    # Photos
    photo_1 = models.ImageField(upload_to="job_photos/%Y/%m/", blank=True)
    photo_2 = models.ImageField(upload_to="job_photos/%Y/%m/", blank=True)
    photo_3 = models.ImageField(upload_to="job_photos/%Y/%m/", blank=True)

    # Assignment
    assigned_contractor = models.ForeignKey(
        ContractorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_jobs",
    )

    # Metadata
    views_count = models.IntegerField(default=0)
    bids_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "category"]),
            models.Index(fields=["city", "county"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("jobs:job_detail", kwargs={"pk": self.pk})


class Bid(models.Model):
    """A contractor's bid on a job."""

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bids")
    contractor = models.ForeignKey(
        ContractorProfile, on_delete=models.CASCADE, related_name="bids",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(help_text="Describe your approach and what's included")
    estimated_duration = models.CharField(max_length=100, blank=True)
    available_start_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["amount"]
        unique_together = ["job", "contractor"]

    def __str__(self):
        return f"${self.amount} bid by {self.contractor.company_name} on {self.job.title}"


class Review(models.Model):
    """Homeowner review of a contractor (Angie's List style ratings)."""

    contractor = models.ForeignKey(
        ContractorProfile, on_delete=models.CASCADE, related_name="reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_written",
    )
    job = models.ForeignKey(
        Job, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews",
    )

    # Angie's List style rating categories
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall grade A(5) through F(1)",
    )
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
    )
    price_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
    )
    punctuality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
    )
    professionalism_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
    )
    responsiveness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
    )

    # Combined average
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    title = models.CharField(max_length=200)
    comment = models.TextField()
    work_description = models.TextField(blank=True, help_text="What work was performed")
    approximate_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    would_hire_again = models.BooleanField(default=True)

    # Photos of completed work
    photo_1 = models.ImageField(upload_to="review_photos/%Y/%m/", blank=True)
    photo_2 = models.ImageField(upload_to="review_photos/%Y/%m/", blank=True)

    # Moderation
    is_verified = models.BooleanField(default=False)
    contractor_response = models.TextField(blank=True)
    contractor_responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["contractor", "reviewer", "job"]

    def __str__(self):
        return f"{self.rating}/5 - {self.title}"

    def save(self, *args, **kwargs):
        # Calculate combined rating
        ratings = [
            self.overall_rating,
            self.quality_rating,
            self.price_rating,
            self.punctuality_rating,
            self.professionalism_rating,
            self.responsiveness_rating,
        ]
        self.rating = sum(ratings) / len(ratings)
        super().save(*args, **kwargs)
        # Update contractor's cached rating
        self.contractor.update_rating_cache()

    @property
    def letter_grade(self):
        """Convert numeric rating to Angie's List style letter grade."""
        if self.rating >= 4.5:
            return "A"
        elif self.rating >= 3.5:
            return "B"
        elif self.rating >= 2.5:
            return "C"
        elif self.rating >= 1.5:
            return "D"
        return "F"


class Message(models.Model):
    """Messages between homeowners and contractors about a job."""

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages",
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender} re: {self.job.title}"
