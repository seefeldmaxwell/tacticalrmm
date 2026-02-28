import { layout } from "./layout";
import type { License, LegalCase, Review, ContractorProfile } from "../types";
import {
  statusBadge,
  starRating,
  formatDate,
  formatCurrency,
  severityBadge,
  letterGrade,
} from "../lib/helpers";

export function licenseDetailPage(
  license: License,
  legalCases: LegalCase[],
  reviews: Review[],
  contractor: ContractorProfile | null
): string {
  const isActive = license.status?.toLowerCase() === "current";

  const legalSection = legalCases.length > 0
    ? legalCases.map((c) => `
      <div class="card mb-2 legal-warning">
        <div class="card-body py-2">
          <div class="d-flex justify-content-between">
            <strong>${c.title || c.case_type}</strong>
            <span>${severityBadge(c.severity)}</span>
          </div>
          <small class="text-muted">${c.case_number || ""} | Filed: ${formatDate(c.filed_date)} | Status: <strong>${c.status}</strong></small>
          ${c.description ? `<p class="mb-1 mt-1 small">${c.description}</p>` : ""}
          <div class="small">
            ${c.fine_amount ? `Fine: <strong class="text-danger">${formatCurrency(c.fine_amount)}</strong>` : ""}
            ${c.license_action && c.license_action !== "None" ? ` | Action: <strong class="text-danger">${c.license_action}</strong>` : ""}
          </div>
        </div>
      </div>`).join("")
    : '<div class="legal-clean p-3 rounded"><i class="bi bi-check-circle text-success"></i> No legal cases or disciplinary actions on record.</div>';

  const avgRating = reviews.length > 0
    ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
    : 0;

  const reviewSection = reviews.length > 0
    ? reviews.map((r) => `
      <div class="card mb-2">
        <div class="card-body py-2">
          <div class="d-flex justify-content-between">
            <strong>${r.title || "Review"}</strong>
            <span>${starRating(r.rating)}</span>
          </div>
          <small class="text-muted">By ${r.reviewer_name || "Anonymous"} on ${formatDate(r.created_at)}</small>
          ${r.comment ? `<p class="mb-0 mt-1">${r.comment}</p>` : ""}
          ${r.would_recommend ? '<small class="text-success"><i class="bi bi-hand-thumbs-up"></i> Would recommend</small>' : ""}
        </div>
      </div>`).join("")
    : '<p class="text-muted">No reviews yet for this license holder.</p>';

  return layout(
    `License ${license.license_number}`,
    `
    <div class="container mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/">Home</a></li>
          <li class="breadcrumb-item"><a href="/search">Search</a></li>
          <li class="breadcrumb-item active">${license.license_number}</li>
        </ol>
      </nav>

      <div class="row">
        <div class="col-md-8">
          <div class="card mb-4">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h2 class="mb-1">${license.licensee_name}</h2>
                  ${license.dba_name ? `<p class="text-muted">DBA: ${license.dba_name}</p>` : ""}
                </div>
                ${avgRating > 0 ? `<span class="grade-badge grade-${letterGrade(avgRating)}">${letterGrade(avgRating)}</span>` : ""}
              </div>
              <table class="table table-sm mt-3">
                <tr><th width="180">License Number</th><td><strong>${license.license_number}</strong></td></tr>
                <tr><th>Status</th><td>${statusBadge(license.status)} ${isActive ? '<small class="text-success ms-2">License is active and in good standing</small>' : ""}</td></tr>
                <tr><th>Trade</th><td>${license.category_name || "—"}</td></tr>
                ${license.rank ? `<tr><th>Rank</th><td>${license.rank}</td></tr>` : ""}
                <tr><th>Location</th><td>${license.city || "—"}, ${license.state} ${license.zip_code || ""} ${license.county ? `(${license.county} County)` : ""}</td></tr>
                ${license.phone ? `<tr><th>Phone</th><td>${license.phone}</td></tr>` : ""}
                ${license.email ? `<tr><th>Email</th><td>${license.email}</td></tr>` : ""}
                <tr><th>Issue Date</th><td>${formatDate(license.issue_date)}</td></tr>
                <tr><th>Expiration Date</th><td>${formatDate(license.expiration_date)}</td></tr>
                <tr><th>Last Verified</th><td>${formatDate(license.last_scraped)}</td></tr>
              </table>
              ${contractor ? `<a href="/contractors/${contractor.id}" class="btn btn-primary">View Contractor Profile</a>` : ""}
            </div>
          </div>

          <div class="card mb-4" id="legal">
            <div class="card-header d-flex justify-content-between">
              <h5 class="mb-0"><i class="bi bi-gavel"></i> Legal Cases & Disciplinary Actions</h5>
              <span class="badge ${legalCases.length > 0 ? "bg-danger" : "bg-success"}">${legalCases.length} case${legalCases.length !== 1 ? "s" : ""}</span>
            </div>
            <div class="card-body">${legalSection}</div>
          </div>

          <div class="card mb-4" id="reviews">
            <div class="card-header d-flex justify-content-between">
              <h5 class="mb-0"><i class="bi bi-star"></i> Reviews & Ratings</h5>
              <span>${starRating(avgRating > 0 ? avgRating : null)} <small>(${reviews.length} reviews)</small></span>
            </div>
            <div class="card-body">${reviewSection}</div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card mb-3 ${legalCases.length > 0 ? "border-danger" : "border-success"}">
            <div class="card-body text-center">
              <h5>License Status</h5>
              <div class="display-6 mb-2">${statusBadge(license.status)}</div>
              ${legalCases.length > 0
                ? `<p class="text-danger mb-0"><i class="bi bi-exclamation-triangle"></i> ${legalCases.length} legal case${legalCases.length !== 1 ? "s" : ""}</p>`
                : '<p class="text-success mb-0"><i class="bi bi-shield-check"></i> Clean record</p>'
              }
            </div>
          </div>

          <div class="card mb-3">
            <div class="card-body">
              <h6>Verify This License</h6>
              <p class="small text-muted">Always verify license information directly with the FL DBPR:</p>
              <a href="https://www.myfloridalicense.com/wl11.asp?mode=2&search=LicNbr&SID=&bession=&licid=&page=1&searchterm=${license.license_number}" target="_blank" class="btn btn-outline-primary btn-sm w-100">
                <i class="bi bi-box-arrow-up-right"></i> Verify on DBPR
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>`,
    "search"
  );
}
