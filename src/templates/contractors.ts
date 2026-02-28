import { layout } from "./layout";
import type { ContractorProfile, Review, LegalCase, TradeCategory } from "../types";
import { statusBadge, starRating, formatDate, formatCurrency, severityBadge, letterGrade } from "../lib/helpers";

export function contractorListPage(
  contractors: ContractorProfile[],
  categories: TradeCategory[],
  selectedCategory: string
): string {
  const filterOptions = categories
    .map(
      (c) =>
        `<option value="${c.slug}" ${selectedCategory === c.slug ? "selected" : ""}>${c.name}</option>`
    )
    .join("");

  const cards = contractors
    .map(
      (c) => `
    <div class="col-md-6 col-lg-4 mb-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
              <h5 class="card-title mb-0">${c.business_name || `${c.first_name} ${c.last_name}`}</h5>
              <small class="text-muted">${c.category_name || "Contractor"}</small>
            </div>
            <span class="grade-badge grade-${letterGrade(c.avg_rating)}">${letterGrade(c.avg_rating)}</span>
          </div>

          <div class="mb-2">${starRating(c.avg_rating)} <small class="text-muted">(${c.total_reviews} reviews)</small></div>

          ${c.license_number
            ? `<div class="mb-2">
                <small>License: <a href="/licenses/${c.license_number}"><strong>${c.license_number}</strong></a></small>
                ${statusBadge(c.license_status || null)}
              </div>`
            : '<div class="mb-2"><small class="text-warning"><i class="bi bi-exclamation-circle"></i> No license linked</small></div>'
          }

          ${legalBadge(c.legal_case_count || 0)}

          <p class="card-text small">${c.bio ? truncate(c.bio, 120) : ""}</p>
          ${c.service_area ? `<small class="text-muted"><i class="bi bi-geo-alt"></i> ${c.service_area}</small><br>` : ""}
          ${c.years_experience ? `<small class="text-muted"><i class="bi bi-clock"></i> ${c.years_experience} years experience</small>` : ""}

          <div class="mt-3">
            <a href="/contractors/${c.id}" class="btn btn-primary btn-sm">View Profile</a>
            ${c.license_number ? `<a href="/licenses/${c.license_number}" class="btn btn-outline-secondary btn-sm">License Info</a>` : ""}
          </div>
        </div>
      </div>
    </div>`
    )
    .join("");

  return layout(
    "Contractors",
    `
    <div class="hero py-4">
      <div class="container">
        <h2>Licensed Contractors</h2>
        <p>Verified Florida licensed contractors with ratings, reviews, and legal case history</p>
      </div>
    </div>
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col-md-6">
          <form action="/contractors" method="get" class="d-flex gap-2">
            <select name="trade" class="form-select">
              <option value="">All Trades</option>
              ${filterOptions}
            </select>
            <button class="btn btn-primary" type="submit">Filter</button>
          </form>
        </div>
      </div>
      <div class="row">
        ${cards || '<div class="col"><p class="text-muted">No verified contractors found.</p></div>'}
      </div>
    </div>`,
    "contractors"
  );
}

export function contractorDetailPage(
  contractor: ContractorProfile,
  reviews: Review[],
  legalCases: LegalCase[]
): string {
  const avgRating = contractor.avg_rating || 0;

  const ratingBreakdown = reviews.length > 0
    ? `
    <div class="row text-center mb-3">
      ${ratingBar("Quality", avgOfField(reviews, "quality_rating"))}
      ${ratingBar("Punctuality", avgOfField(reviews, "punctuality_rating"))}
      ${ratingBar("Price", avgOfField(reviews, "price_rating"))}
      ${ratingBar("Professionalism", avgOfField(reviews, "professionalism_rating"))}
      ${ratingBar("Communication", avgOfField(reviews, "communication_rating"))}
    </div>`
    : "";

  const reviewCards = reviews
    .map(
      (r) => `
    <div class="card mb-2">
      <div class="card-body py-2">
        <div class="d-flex justify-content-between">
          <strong>${r.title || "Review"}</strong>
          ${starRating(r.rating)}
        </div>
        <small class="text-muted">By ${r.reviewer_name || "Anonymous"} on ${formatDate(r.created_at)}</small>
        ${r.comment ? `<p class="mb-1 mt-1">${r.comment}</p>` : ""}
        ${r.would_recommend ? '<small class="text-success"><i class="bi bi-hand-thumbs-up"></i> Recommends</small>' : ""}
      </div>
    </div>`
    )
    .join("");

  const legalSection = legalCases.length > 0
    ? legalCases.map((c) => `
      <div class="card mb-2 legal-warning">
        <div class="card-body py-2">
          <div class="d-flex justify-content-between">
            <strong>${c.title || c.case_type}</strong>
            ${severityBadge(c.severity)}
          </div>
          <small class="text-muted">${c.case_number || ""} | Filed: ${formatDate(c.filed_date)} | Status: <strong>${c.status}</strong></small>
          ${c.description ? `<p class="mb-1 mt-1 small">${c.description}</p>` : ""}
          <div class="small">
            ${c.fine_amount ? `Fine: <strong class="text-danger">${formatCurrency(c.fine_amount)}</strong>` : ""}
            ${c.license_action && c.license_action !== "None" ? ` | Action: <strong class="text-danger">${c.license_action}</strong>` : ""}
          </div>
        </div>
      </div>`).join("")
    : '<div class="legal-clean p-3 rounded"><i class="bi bi-check-circle text-success"></i> No legal cases or disciplinary actions.</div>';

  return layout(
    contractor.business_name || "Contractor",
    `
    <div class="container mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/">Home</a></li>
          <li class="breadcrumb-item"><a href="/contractors">Contractors</a></li>
          <li class="breadcrumb-item active">${contractor.business_name || `${contractor.first_name} ${contractor.last_name}`}</li>
        </ol>
      </nav>

      <div class="row">
        <div class="col-md-8">
          <div class="card mb-4">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h2 class="mb-1">${contractor.business_name || `${contractor.first_name} ${contractor.last_name}`}</h2>
                  <p class="text-muted">${contractor.category_name || "Contractor"}</p>
                </div>
                <span class="grade-badge grade-${letterGrade(avgRating)}">${letterGrade(avgRating)}</span>
              </div>
              <div class="mb-3">${starRating(avgRating)} <small class="text-muted">(${contractor.total_reviews} reviews)</small></div>
              ${contractor.bio ? `<p>${contractor.bio}</p>` : ""}
              <div class="row">
                ${contractor.service_area ? `<div class="col-md-6"><small class="text-muted"><i class="bi bi-geo-alt"></i> ${contractor.service_area}</small></div>` : ""}
                ${contractor.years_experience ? `<div class="col-md-6"><small class="text-muted"><i class="bi bi-clock"></i> ${contractor.years_experience} years experience</small></div>` : ""}
                ${contractor.website ? `<div class="col-md-6"><small><a href="${contractor.website}" target="_blank"><i class="bi bi-globe"></i> Website</a></small></div>` : ""}
              </div>
            </div>
          </div>

          ${ratingBreakdown ? `<div class="card mb-4"><div class="card-header"><h5 class="mb-0">Rating Breakdown</h5></div><div class="card-body">${ratingBreakdown}</div></div>` : ""}

          <div class="card mb-4" id="legal">
            <div class="card-header d-flex justify-content-between">
              <h5 class="mb-0"><i class="bi bi-gavel"></i> Legal Cases</h5>
              <span class="badge ${legalCases.length > 0 ? "bg-danger" : "bg-success"}">${legalCases.length}</span>
            </div>
            <div class="card-body">${legalSection}</div>
          </div>

          <div class="card mb-4" id="reviews">
            <div class="card-header d-flex justify-content-between">
              <h5 class="mb-0"><i class="bi bi-star"></i> Reviews</h5>
              <span>${starRating(avgRating)} (${reviews.length})</span>
            </div>
            <div class="card-body">${reviewCards || '<p class="text-muted">No reviews yet.</p>'}</div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card mb-3 ${contractor.is_verified ? "border-success" : "border-warning"}">
            <div class="card-body text-center">
              <h5>${contractor.is_verified ? '<i class="bi bi-patch-check text-success"></i> Verified' : '<i class="bi bi-question-circle text-warning"></i> Unverified'}</h5>
              ${contractor.license_number
                ? `<p class="mb-1">License: <a href="/licenses/${contractor.license_number}"><strong>${contractor.license_number}</strong></a></p>
                   <div>${statusBadge(contractor.license_status || null)}</div>`
                : '<p class="text-muted">No license linked</p>'
              }
            </div>
          </div>

          <div class="card mb-3 ${legalCases.length > 0 ? "border-danger" : "border-success"}">
            <div class="card-body text-center">
              ${legalCases.length > 0
                ? `<p class="text-danger mb-0"><i class="bi bi-exclamation-triangle"></i> <strong>${legalCases.length}</strong> legal case${legalCases.length !== 1 ? "s" : ""} on file</p>`
                : '<p class="text-success mb-0"><i class="bi bi-shield-check"></i> Clean record</p>'
              }
            </div>
          </div>
        </div>
      </div>
    </div>`,
    "contractors"
  );
}

function legalBadge(count: number): string {
  if (count > 0)
    return `<div class="legal-warning p-2 rounded mb-2"><small><i class="bi bi-exclamation-triangle text-danger"></i> <strong>${count}</strong> legal case${count > 1 ? "s" : ""}</small></div>`;
  return `<div class="legal-clean p-2 rounded mb-2"><small><i class="bi bi-check-circle text-success"></i> No legal cases</small></div>`;
}

function truncate(text: string, len: number): string {
  return text.length <= len ? text : text.substring(0, len) + "...";
}

function avgOfField(reviews: Review[], field: string): number {
  const vals = reviews
    .map((r) => (r as unknown as Record<string, unknown>)[field] as number | null)
    .filter((v): v is number => v !== null && v !== undefined);
  if (vals.length === 0) return 0;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

function ratingBar(label: string, value: number): string {
  if (value <= 0) return "";
  const pct = (value / 5) * 100;
  return `
    <div class="col">
      <small class="text-muted">${label}</small>
      <div class="progress" style="height: 8px;">
        <div class="progress-bar bg-warning" style="width: ${pct}%"></div>
      </div>
      <small>${value.toFixed(1)}</small>
    </div>`;
}
