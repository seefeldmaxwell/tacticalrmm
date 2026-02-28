"""Forms for user accounts."""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class ProfileForm(forms.ModelForm):
    """User profile edit form."""

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email",
            "phone", "city", "county", "zip_code",
            "avatar", "email_notifications",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "county": forms.TextInput(attrs={"class": "form-control"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control"}),
            "email_notifications": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ContractorRegistrationForm(UserCreationForm):
    """Registration form for contractors with license number."""

    license_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your Florida license number (e.g., EC13012345)",
        }),
        help_text="We'll verify this against the Florida DBPR database.",
    )
    company_name = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your business name",
        }),
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "first_name", "last_name",
            "password1", "password2", "phone", "city", "county",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "county": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "contractor"
        if commit:
            user.save()
            # Create contractor profile
            from fl_license_scraper.jobs.models import ContractorProfile
            from fl_license_scraper.scraper.scraper_engine import lookup_license

            license_obj = lookup_license(self.cleaned_data["license_number"])
            ContractorProfile.objects.create(
                user=user,
                license=license_obj,
                company_name=self.cleaned_data["company_name"],
                city=user.city,
                county=user.county,
                is_verified=license_obj is not None and license_obj.is_active,
            )
        return user
