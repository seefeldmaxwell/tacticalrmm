"""Account views for profile and registration."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, ContractorRegistrationForm


@login_required
def profile(request):
    """User profile view."""
    return render(request, "accounts/profile.html")


@login_required
def profile_edit(request):
    """Edit user profile."""
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


def contractor_register(request):
    """Contractor registration with license verification."""
    if request.method == "POST":
        form = ContractorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("accounts:profile")
    else:
        form = ContractorRegistrationForm()
    return render(request, "accounts/contractor_register.html", {"form": form})
