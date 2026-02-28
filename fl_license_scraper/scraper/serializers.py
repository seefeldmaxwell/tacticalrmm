"""API serializers for license data."""
from rest_framework import serializers
from .models import License, LicenseHistory, TradeCategory


class TradeCategorySerializer(serializers.ModelSerializer):
    license_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = TradeCategory
        fields = ["id", "name", "slug", "description", "dbpr_code", "icon", "license_count"]


class LicenseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseHistory
        fields = ["field_changed", "old_value", "new_value", "changed_at"]


class LicenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default="")
    is_active = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    has_legal_cases = serializers.BooleanField(read_only=True)
    legal_case_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = License
        fields = [
            "id", "license_number", "license_type", "status", "rank",
            "category", "category_name",
            "licensee_name", "business_name", "dba_name",
            "address_line1", "address_line2", "city", "state",
            "zip_code", "county", "phone", "email",
            "original_issue_date", "effective_date",
            "expiration_date", "last_renewal_date",
            "qualifier_name", "dbpr_url",
            "is_active", "is_expired",
            "has_legal_cases", "legal_case_count",
            "last_scraped", "created_at", "updated_at",
        ]


class LicenseDetailSerializer(LicenseSerializer):
    history = LicenseHistorySerializer(many=True, read_only=True)

    class Meta(LicenseSerializer.Meta):
        fields = LicenseSerializer.Meta.fields + ["history"]
