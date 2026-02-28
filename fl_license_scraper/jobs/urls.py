"""URL routes for the job board."""
from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    # Jobs
    path("", views.job_list, name="job_list"),
    path("post/", views.job_create, name="job_create"),
    path("<int:pk>/", views.job_detail, name="job_detail"),
    path("<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("<int:job_pk>/bid/", views.bid_submit, name="bid_submit"),
    # Contractors
    path("contractors/", views.contractor_list, name="contractor_list"),
    path("contractors/<int:pk>/", views.contractor_detail, name="contractor_detail"),
    path("contractors/<int:contractor_pk>/review/", views.review_create, name="review_create"),
    # Dashboard
    path("dashboard/", views.my_dashboard, name="dashboard"),
]
