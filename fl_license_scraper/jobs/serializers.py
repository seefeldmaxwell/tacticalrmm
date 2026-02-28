"""API serializers for the job board."""
from rest_framework import serializers
from .models import Bid, ContractorProfile, Job, Review


class ContractorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    license_number = serializers.CharField(source="license.license_number", read_only=True, default="")
    license_status = serializers.CharField(source="license.status", read_only=True, default="")
    specialties = serializers.StringRelatedField(many=True, read_only=True)
    letter_grade = serializers.SerializerMethodField()

    class Meta:
        model = ContractorProfile
        fields = [
            "id", "username", "company_name", "tagline", "description",
            "website", "phone", "email",
            "city", "county", "zip_code", "service_radius_miles",
            "specialties", "years_experience",
            "license_number", "license_status",
            "insurance_verified", "bonded",
            "is_verified", "is_featured", "membership_level",
            "avg_rating", "total_reviews", "jobs_completed",
            "response_time_hours", "letter_grade",
            "created_at",
        ]

    def get_letter_grade(self, obj):
        rating = float(obj.avg_rating)
        if rating >= 4.5:
            return "A"
        elif rating >= 3.5:
            return "B"
        elif rating >= 2.5:
            return "C"
        elif rating >= 1.5:
            return "D"
        return "F"


class JobSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source="posted_by.get_full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default="")

    class Meta:
        model = Job
        fields = [
            "id", "title", "description", "category", "category_name",
            "status", "posted_by_name",
            "city", "county", "zip_code",
            "urgency", "budget_range", "preferred_start_date",
            "requires_license",
            "views_count", "bids_count",
            "created_at", "updated_at",
        ]


class BidSerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source="contractor.company_name", read_only=True)

    class Meta:
        model = Bid
        fields = [
            "id", "job", "contractor", "contractor_name",
            "amount", "description", "estimated_duration",
            "available_start_date", "status",
            "created_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.get_full_name", read_only=True)
    letter_grade = serializers.CharField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "contractor", "reviewer_name", "job",
            "overall_rating", "quality_rating", "price_rating",
            "punctuality_rating", "professionalism_rating", "responsiveness_rating",
            "rating", "letter_grade",
            "title", "comment", "work_description",
            "approximate_cost", "would_hire_again",
            "is_verified", "contractor_response",
            "created_at",
        ]
