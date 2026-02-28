"""Forms for the job board."""

from django import forms

from .models import Bid, Job, Review


class JobForm(forms.ModelForm):
    """Form for creating/editing a job posting."""

    class Meta:
        model = Job
        fields = [
            "title", "description", "category",
            "city", "county", "zip_code", "address",
            "urgency", "budget_range", "preferred_start_date",
            "requires_license",
            "photo_1", "photo_2", "photo_3",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Kitchen remodel, AC repair, Electrical panel upgrade",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Describe the work you need done in detail...",
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "county": forms.TextInput(attrs={"class": "form-control", "placeholder": "County"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "ZIP"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Address (optional)"}),
            "urgency": forms.Select(attrs={"class": "form-select"}),
            "budget_range": forms.Select(attrs={"class": "form-select"}),
            "preferred_start_date": forms.DateInput(attrs={
                "class": "form-control", "type": "date",
            }),
            "requires_license": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class BidForm(forms.ModelForm):
    """Form for contractors to submit a bid."""

    class Meta:
        model = Bid
        fields = ["amount", "description", "estimated_duration", "available_start_date"]
        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Your bid amount in dollars",
                "step": "0.01",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe your approach, materials, and what's included...",
            }),
            "estimated_duration": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., 2-3 days, 1 week",
            }),
            "available_start_date": forms.DateInput(attrs={
                "class": "form-control", "type": "date",
            }),
        }


class ReviewForm(forms.ModelForm):
    """Form for homeowners to review a contractor."""

    class Meta:
        model = Review
        fields = [
            "title", "comment", "work_description",
            "overall_rating", "quality_rating", "price_rating",
            "punctuality_rating", "professionalism_rating", "responsiveness_rating",
            "approximate_cost", "would_hire_again",
            "photo_1", "photo_2",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Summary of your experience",
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe your experience in detail...",
            }),
            "work_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "What work was performed?",
            }),
            "overall_rating": forms.Select(
                choices=[(i, f"{i} - {'ABCDF'[5-i]}") for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "quality_rating": forms.Select(
                choices=[(i, str(i)) for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "price_rating": forms.Select(
                choices=[(i, str(i)) for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "punctuality_rating": forms.Select(
                choices=[(i, str(i)) for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "professionalism_rating": forms.Select(
                choices=[(i, str(i)) for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "responsiveness_rating": forms.Select(
                choices=[(i, str(i)) for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "approximate_cost": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Approximate cost of work",
                "step": "0.01",
            }),
            "would_hire_again": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
