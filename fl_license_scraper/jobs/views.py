"""Views for the job board - Angie's List style marketplace."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from fl_license_scraper.scraper.models import TradeCategory

from .forms import BidForm, JobForm, ReviewForm
from .models import Bid, ContractorProfile, Job, Review


def job_list(request):
    """Browse open jobs - main job board view."""
    category_slug = request.GET.get("category", "")
    county = request.GET.get("county", "")
    city = request.GET.get("city", "")
    urgency = request.GET.get("urgency", "")
    budget = request.GET.get("budget", "")
    query = request.GET.get("q", "").strip()

    jobs = Job.objects.filter(status="open").select_related("posted_by", "category")

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        jobs = jobs.filter(category__slug=category_slug)
    if county:
        jobs = jobs.filter(county__iexact=county)
    if city:
        jobs = jobs.filter(city__iexact=city)
    if urgency:
        jobs = jobs.filter(urgency=urgency)
    if budget:
        jobs = jobs.filter(budget_range=budget)

    jobs = jobs.order_by("-created_at")[:50]

    categories = TradeCategory.objects.annotate(
        job_count=Count("jobs", filter=Q(jobs__status="open"))
    ).order_by("name")

    context = {
        "jobs": jobs,
        "categories": categories,
        "query": query,
        "category_slug": category_slug,
        "county": county,
        "city": city,
        "urgency": urgency,
        "budget": budget,
        "urgency_choices": Job.URGENCY_CHOICES,
        "budget_choices": Job.BUDGET_CHOICES,
    }
    return render(request, "jobs/job_list.html", context)


def job_detail(request, pk):
    """View a specific job posting with bids."""
    job = get_object_or_404(Job.objects.select_related("posted_by", "category"), pk=pk)

    # Increment view count
    Job.objects.filter(pk=pk).update(views_count=models.F("views_count") + 1)

    bids = job.bids.select_related("contractor").order_by("amount")
    user_bid = None
    if request.user.is_authenticated and hasattr(request.user, "contractor_profile"):
        user_bid = bids.filter(contractor=request.user.contractor_profile).first()

    context = {
        "job": job,
        "bids": bids if request.user == job.posted_by else bids[:3],
        "user_bid": user_bid,
        "bid_form": BidForm() if not user_bid else None,
    }
    return render(request, "jobs/job_detail.html", context)


@login_required
def job_create(request):
    """Create a new job posting."""
    if request.method == "POST":
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully! Contractors can now bid.")
            return redirect("jobs:job_detail", pk=job.pk)
    else:
        form = JobForm()

    categories = TradeCategory.objects.order_by("name")
    context = {"form": form, "categories": categories}
    return render(request, "jobs/job_create.html", context)


@login_required
def job_edit(request, pk):
    """Edit an existing job posting."""
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)

    if request.method == "POST":
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("jobs:job_detail", pk=job.pk)
    else:
        form = JobForm(instance=job)

    context = {"form": form, "job": job}
    return render(request, "jobs/job_edit.html", context)


@login_required
def bid_submit(request, job_pk):
    """Submit a bid on a job (contractors only)."""
    job = get_object_or_404(Job, pk=job_pk, status="open")

    if not hasattr(request.user, "contractor_profile"):
        messages.error(request, "Only registered contractors can submit bids.")
        return redirect("jobs:job_detail", pk=job.pk)

    contractor = request.user.contractor_profile

    if Bid.objects.filter(job=job, contractor=contractor).exists():
        messages.warning(request, "You already have a bid on this job.")
        return redirect("jobs:job_detail", pk=job.pk)

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.job = job
            bid.contractor = contractor
            bid.save()
            Job.objects.filter(pk=job.pk).update(
                bids_count=models.F("bids_count") + 1
            )
            messages.success(request, "Bid submitted successfully!")
            return redirect("jobs:job_detail", pk=job.pk)
    else:
        form = BidForm()

    context = {"form": form, "job": job}
    return render(request, "jobs/bid_submit.html", context)


def contractor_list(request):
    """Browse contractors - Angie's List style directory."""
    category_slug = request.GET.get("category", "")
    county = request.GET.get("county", "")
    city = request.GET.get("city", "")
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "rating")

    contractors = ContractorProfile.objects.filter(
        is_verified=True
    ).select_related("user", "license")

    if query:
        contractors = contractors.filter(
            Q(company_name__icontains=query)
            | Q(description__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )
    if category_slug:
        contractors = contractors.filter(specialties__slug=category_slug)
    if county:
        contractors = contractors.filter(county__iexact=county)
    if city:
        contractors = contractors.filter(city__iexact=city)

    if sort == "rating":
        contractors = contractors.order_by("-avg_rating", "-total_reviews")
    elif sort == "reviews":
        contractors = contractors.order_by("-total_reviews")
    elif sort == "experience":
        contractors = contractors.order_by("-years_experience")
    else:
        contractors = contractors.order_by("-avg_rating")

    contractors = contractors[:50]

    categories = TradeCategory.objects.annotate(
        contractor_count=Count("contractors")
    ).order_by("name")

    context = {
        "contractors": contractors,
        "categories": categories,
        "query": query,
        "category_slug": category_slug,
        "county": county,
        "city": city,
        "sort": sort,
    }
    return render(request, "jobs/contractor_list.html", context)


def contractor_detail(request, pk):
    """View a contractor's profile with reviews."""
    contractor = get_object_or_404(
        ContractorProfile.objects.select_related("user", "license"),
        pk=pk,
    )
    reviews = contractor.reviews.select_related("reviewer", "job").order_by("-created_at")[:20]
    portfolio = contractor.portfolio.order_by("-created_at")[:12]
    legal_cases = []
    if contractor.license:
        legal_cases = contractor.license.legal_cases.order_by("-filed_date")[:5]

    # Rating breakdown
    rating_breakdown = {}
    for i in range(5, 0, -1):
        count = contractor.reviews.filter(overall_rating=i).count()
        rating_breakdown[i] = {
            "count": count,
            "pct": (count / contractor.total_reviews * 100) if contractor.total_reviews > 0 else 0,
        }

    context = {
        "contractor": contractor,
        "reviews": reviews,
        "portfolio": portfolio,
        "legal_cases": legal_cases,
        "rating_breakdown": rating_breakdown,
        "review_form": ReviewForm() if request.user.is_authenticated else None,
    }
    return render(request, "jobs/contractor_detail.html", context)


@login_required
def review_create(request, contractor_pk):
    """Write a review for a contractor."""
    contractor = get_object_or_404(ContractorProfile, pk=contractor_pk)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.contractor = contractor
            review.reviewer = request.user
            review.save()
            messages.success(request, "Review submitted! Thank you for your feedback.")
            return redirect("jobs:contractor_detail", pk=contractor.pk)
    else:
        form = ReviewForm()

    context = {"form": form, "contractor": contractor}
    return render(request, "jobs/review_create.html", context)


@login_required
def my_dashboard(request):
    """Dashboard for logged-in users showing their jobs/bids."""
    context = {
        "my_jobs": Job.objects.filter(posted_by=request.user).order_by("-created_at")[:10],
    }

    if hasattr(request.user, "contractor_profile"):
        contractor = request.user.contractor_profile
        context.update({
            "contractor": contractor,
            "my_bids": Bid.objects.filter(contractor=contractor).select_related("job").order_by("-created_at")[:10],
            "my_reviews": contractor.reviews.order_by("-created_at")[:10],
        })

    return render(request, "jobs/dashboard.html", context)
