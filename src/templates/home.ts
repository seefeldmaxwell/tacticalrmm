import { layout } from "./layout";
import type { ContractorProfile, TradeCategory } from "../types";
import { statusBadge, starRating } from "../lib/helpers";

export function homePage(
  stats: { licenses: number; contractors: number; jobs: number; trades: number },
  featuredContractors: ContractorProfile[],
  categories: TradeCategory[]
): string {
  const contractorCards = featuredContractors
    .map(
      (c) => `
    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <h5 class="card-title mb-1">${c.business_name || `${c.first_name} ${c.last_name}`}</h5>
            <span class="grade-badge grade-${gradeClass(c.avg_rating)}">${letterG(c.avg_rating)}</span>
          </div>
          <p class="text-muted mb-1">${c.category_name || "Contractor"}</p>
          <div class="mb-2">${starRating(c.avg_rating)} <small class="text-muted">(${c.total_reviews} reviews)</small></div>
          <div class="mb-2">
            ${c.license_number ? `<small>License: <strong>${c.license_number}</strong></small> ${statusBadge(c.license_status || null)}` : ""}
          </div>
          ${legalBadge(c.legal_case_count || 0)}
          <a href="/contractors/${c.id}" class="btn btn-outline-primary btn-sm mt-2">View Profile</a>
        </div>
      </div>
    </div>`
    )
    .join("");

  const categoryList = categories
    .map(
      (cat) => `
    <a href="/trades/${cat.slug}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
      <span><i class="bi bi-${iconMap(cat.icon)}"></i> ${cat.name}</span>
      <span class="badge bg-primary">${cat.prefix}</span>
    </a>`
    )
    .join("");

  return layout(
    "Home",
    `
    <div class="hero">
      <div class="container text-center">
        <h1 class="display-5 fw-bold">Florida Licensed Contractor Search</h1>
        <p class="lead">Verify licenses, check legal cases, read reviews, and hire trusted contractors</p>
        <div class="search-box mt-4">
          <form action="/search" method="get">
            <div class="input-group input-group-lg">
              <input type="text" class="form-control" name="q" placeholder="Search by license number, name, or trade...">
              <button class="btn btn-warning" type="submit"><i class="bi bi-search"></i> Search</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div class="container mt-4">
      <div class="row g-3 mb-4">
        <div class="col-md-3"><div class="card stat-card"><h3>${stats.licenses}</h3><p class="text-muted mb-0">Licenses Tracked</p></div></div>
        <div class="col-md-3"><div class="card stat-card"><h3>${stats.contractors}</h3><p class="text-muted mb-0">Verified Contractors</p></div></div>
        <div class="col-md-3"><div class="card stat-card"><h3>${stats.jobs}</h3><p class="text-muted mb-0">Open Jobs</p></div></div>
        <div class="col-md-3"><div class="card stat-card"><h3>${stats.trades}</h3><p class="text-muted mb-0">Trade Categories</p></div></div>
      </div>

      <div class="row">
        <div class="col-md-8">
          <h3 class="mb-3">Featured Contractors</h3>
          <div class="row">${contractorCards || '<div class="col"><p class="text-muted">No contractors yet. Be the first to register!</p></div>'}</div>
        </div>
        <div class="col-md-4">
          <h3 class="mb-3">Trade Categories</h3>
          <div class="list-group">${categoryList}</div>
        </div>
      </div>
    </div>`,
    "home"
  );
}

function letterG(rating: number | null): string {
  if (!rating || rating <= 0) return "N/A";
  if (rating >= 4.5) return "A";
  if (rating >= 3.5) return "B";
  if (rating >= 2.5) return "C";
  if (rating >= 1.5) return "D";
  return "F";
}

function gradeClass(rating: number | null): string {
  return letterG(rating).replace("/", "");
}

function legalBadge(count: number): string {
  if (count > 0)
    return `<div class="legal-warning p-2 rounded mb-2"><small><i class="bi bi-exclamation-triangle text-danger"></i> <strong>${count}</strong> legal case${count > 1 ? "s" : ""} on file</small></div>`;
  return `<div class="legal-clean p-2 rounded mb-2"><small><i class="bi bi-check-circle text-success"></i> No legal cases</small></div>`;
}

function iconMap(icon: string): string {
  const map: Record<string, string> = {
    zap: "lightning-charge",
    droplet: "droplet",
    thermometer: "thermometer-half",
    "hard-hat": "building",
    home: "house-door",
    building: "buildings",
    layers: "layers",
    sun: "sun",
    waves: "water",
    shield: "shield-check",
    square: "grid",
    settings: "gear",
    scissors: "scissors",
    paintbrush: "brush",
    bell: "bell",
    wrench: "wrench",
  };
  return map[icon] || "wrench";
}
