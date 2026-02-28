import { layout } from "./layout";
import type { Job, Bid, TradeCategory } from "../types";
import {
  statusBadge,
  starRating,
  formatDate,
  formatCurrency,
  urgencyBadge,
  jobStatusBadge,
  severityBadge,
} from "../lib/helpers";

export function jobListPage(
  jobs: Job[],
  categories: TradeCategory[],
  selectedCategory: string,
  selectedStatus: string
): string {
  const catOptions = categories
    .map(
      (c) =>
        `<option value="${c.slug}" ${selectedCategory === c.slug ? "selected" : ""}>${c.name}</option>`
    )
    .join("");

  const jobCards = jobs
    .map(
      (j) => `
    <div class="col-md-6 mb-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="card-title mb-0"><a href="/jobs/${j.id}" class="text-decoration-none">${j.title}</a></h5>
            <div>${jobStatusBadge(j.status)} ${urgencyBadge(j.urgency)}</div>
          </div>
          <p class="text-muted small mb-2">${j.category_name || "General"} | ${j.city || "Florida"} | Posted ${formatDate(j.created_at)}</p>
          <p class="card-text">${truncate(j.description, 150)}</p>
          <div class="d-flex justify-content-between align-items-center">
            <div>
              ${j.budget_min || j.budget_max ? `<strong>${formatCurrency(j.budget_min)} - ${formatCurrency(j.budget_max)}</strong>` : '<span class="text-muted">Budget not specified</span>'}
            </div>
            <div>
              ${j.requires_license ? '<span class="badge bg-info">License Required</span>' : ""}
              ${j.bid_count !== undefined ? `<span class="badge bg-secondary">${j.bid_count} bid${j.bid_count !== 1 ? "s" : ""}</span>` : ""}
            </div>
          </div>
          <a href="/jobs/${j.id}" class="btn btn-outline-primary btn-sm mt-2">View Details</a>
        </div>
      </div>
    </div>`
    )
    .join("");

  return layout(
    "Job Board",
    `
    <div class="hero py-4">
      <div class="container">
        <h2>Job Board</h2>
        <p>Find and post home improvement jobs. Connect with licensed Florida contractors.</p>
      </div>
    </div>
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col-md-8">
          <form action="/jobs" method="get" class="d-flex gap-2">
            <select name="trade" class="form-select">
              <option value="">All Trades</option>
              ${catOptions}
            </select>
            <select name="status" class="form-select">
              <option value="" ${!selectedStatus ? "selected" : ""}>All Status</option>
              <option value="open" ${selectedStatus === "open" ? "selected" : ""}>Open</option>
              <option value="in_progress" ${selectedStatus === "in_progress" ? "selected" : ""}>In Progress</option>
              <option value="completed" ${selectedStatus === "completed" ? "selected" : ""}>Completed</option>
            </select>
            <button class="btn btn-primary" type="submit">Filter</button>
          </form>
        </div>
      </div>
      <div class="row">
        ${jobCards || '<div class="col"><p class="text-muted">No jobs found.</p></div>'}
      </div>
    </div>`,
    "jobs"
  );
}

export function jobDetailPage(
  job: Job,
  bids: Bid[]
): string {
  const bidCards = bids
    .map(
      (b) => `
    <div class="card mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <h5 class="mb-1">${b.business_name || b.contractor_name || "Contractor"}</h5>
            <div class="mb-1">${starRating(b.avg_rating || null)} <small>(${b.total_reviews || 0} reviews)</small></div>
          </div>
          <div class="text-end">
            <h4 class="text-primary mb-0">${formatCurrency(b.amount)}</h4>
            ${b.estimated_days ? `<small class="text-muted">${b.estimated_days} days</small>` : ""}
          </div>
        </div>

        ${b.license_number
          ? `<div class="mb-2">
              <small>License: <a href="/licenses/${b.license_number}"><strong>${b.license_number}</strong></a></small>
              ${statusBadge(b.license_status || null)}
            </div>`
          : '<div class="mb-2"><small class="text-warning"><i class="bi bi-exclamation-circle"></i> No license</small></div>'
        }

        ${legalBidBadge(b.legal_case_count || 0, b.license_number)}

        ${b.message ? `<p class="mb-1">${b.message}</p>` : ""}
        <span class="badge ${b.status === "accepted" ? "bg-success" : b.status === "rejected" ? "bg-danger" : "bg-secondary"}">${b.status}</span>
      </div>
    </div>`
    )
    .join("");

  return layout(
    job.title,
    `
    <div class="container mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/">Home</a></li>
          <li class="breadcrumb-item"><a href="/jobs">Jobs</a></li>
          <li class="breadcrumb-item active">${job.title}</li>
        </ol>
      </nav>

      <div class="row">
        <div class="col-md-8">
          <div class="card mb-4">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <h2 class="mb-1">${job.title}</h2>
                <div>${jobStatusBadge(job.status)} ${urgencyBadge(job.urgency)}</div>
              </div>
              <p class="text-muted">${job.category_name || "General"} | ${job.city || "Florida"} | Posted by ${job.poster_name || "Homeowner"}</p>
              <p>${job.description}</p>
              <div class="row">
                <div class="col-md-4">
                  <strong>Budget:</strong> ${job.budget_min || job.budget_max ? `${formatCurrency(job.budget_min)} - ${formatCurrency(job.budget_max)}` : "Not specified"}
                </div>
                <div class="col-md-4">
                  <strong>Posted:</strong> ${formatDate(job.created_at)}
                </div>
                <div class="col-md-4">
                  ${job.requires_license ? '<span class="badge bg-info">License Required</span>' : ""}
                </div>
              </div>
            </div>
          </div>

          <h4 class="mb-3">Bids (${bids.length})</h4>
          ${bidCards || '<p class="text-muted">No bids yet. Be the first to bid!</p>'}
        </div>

        <div class="col-md-4">
          <div class="card mb-3">
            <div class="card-body text-center">
              <h5>Job Summary</h5>
              <p class="mb-1"><strong>${bids.length}</strong> bid${bids.length !== 1 ? "s" : ""}</p>
              <p class="mb-1">${jobStatusBadge(job.status)}</p>
              <p class="mb-0">${urgencyBadge(job.urgency)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>`,
    "jobs"
  );
}

function legalBidBadge(count: number, licNum: string | undefined): string {
  if (count > 0)
    return `<div class="legal-warning p-2 rounded mb-2"><small><i class="bi bi-exclamation-triangle text-danger"></i> <strong>${count}</strong> legal case${count > 1 ? "s" : ""} ${licNum ? `<a href="/licenses/${licNum}#legal">View</a>` : ""}</small></div>`;
  return `<div class="legal-clean p-2 rounded mb-2"><small><i class="bi bi-check-circle text-success"></i> No legal cases</small></div>`;
}

function truncate(text: string, len: number): string {
  return text.length <= len ? text : text.substring(0, len) + "...";
}
