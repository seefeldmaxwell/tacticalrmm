import { layout } from "./layout";
import type { TradeCategory, License } from "../types";
import { statusBadge, starRating, formatDate } from "../lib/helpers";

export function tradeListPage(categories: TradeCategory[]): string {
  const cards = categories
    .map(
      (c) => `
    <div class="col-md-4 col-lg-3 mb-4">
      <a href="/trades/${c.slug}" class="text-decoration-none">
        <div class="card h-100 text-center">
          <div class="card-body">
            <i class="bi bi-${iconMap(c.icon)} display-4 text-primary"></i>
            <h5 class="mt-2">${c.name}</h5>
            <p class="text-muted small">${c.description || ""}</p>
            <span class="badge bg-primary">${c.prefix}</span>
          </div>
        </div>
      </a>
    </div>`
    )
    .join("");

  return layout(
    "Trade Categories",
    `
    <div class="hero py-4">
      <div class="container">
        <h2>Florida Trade Categories</h2>
        <p>Browse all licensed skilled trade categories regulated by the Florida DBPR</p>
      </div>
    </div>
    <div class="container mt-4">
      <div class="row">${cards}</div>
    </div>`,
    "trades"
  );
}

export function tradeDetailPage(
  category: TradeCategory,
  licenses: License[]
): string {
  const rows = licenses
    .map(
      (l) => `
    <tr>
      <td><a href="/licenses/${l.license_number}"><strong>${l.license_number}</strong></a></td>
      <td>${l.licensee_name}</td>
      <td>${statusBadge(l.status)}</td>
      <td>${l.city || "—"}</td>
      <td>${starRating(l.avg_rating || null)} ${l.review_count ? `<small>(${l.review_count})</small>` : ""}</td>
      <td>${legalCol(l.legal_case_count || 0, l.license_number)}</td>
      <td><small>${formatDate(l.expiration_date || null)}</small></td>
    </tr>`
    )
    .join("");

  return layout(
    category.name,
    `
    <div class="container mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/">Home</a></li>
          <li class="breadcrumb-item"><a href="/trades">Trades</a></li>
          <li class="breadcrumb-item active">${category.name}</li>
        </ol>
      </nav>

      <div class="card mb-4">
        <div class="card-body">
          <h2><i class="bi bi-${iconMap(category.icon)}"></i> ${category.name}</h2>
          <p class="text-muted">${category.description || ""}</p>
          <div class="row">
            <div class="col-md-3"><strong>Board:</strong> ${category.board_name}</div>
            <div class="col-md-3"><strong>Code:</strong> ${category.license_code}</div>
            <div class="col-md-3"><strong>Prefix:</strong> ${category.prefix}</div>
            <div class="col-md-3"><strong>Licenses:</strong> ${licenses.length}</div>
          </div>
        </div>
      </div>

      ${
        licenses.length > 0
          ? `
      <div class="table-responsive">
        <table class="table table-hover bg-white rounded">
          <thead class="table-light">
            <tr>
              <th>License #</th>
              <th>Name</th>
              <th>Status</th>
              <th>City</th>
              <th>Reviews</th>
              <th>Legal Cases</th>
              <th>Expires</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`
          : '<div class="alert alert-info">No licenses found for this trade category yet. Use the search to look up specific licenses.</div>'
      }
    </div>`,
    "trades"
  );
}

function legalCol(count: number, licNum: string): string {
  if (count > 0)
    return `<a href="/licenses/${licNum}#legal" class="text-danger text-decoration-none"><i class="bi bi-exclamation-triangle"></i> ${count}</a>`;
  return '<span class="text-success"><i class="bi bi-check-circle"></i> Clean</span>';
}

function iconMap(icon: string): string {
  const map: Record<string, string> = {
    zap: "lightning-charge", droplet: "droplet", thermometer: "thermometer-half",
    "hard-hat": "building", home: "house-door", building: "buildings",
    layers: "layers", sun: "sun", waves: "water", shield: "shield-check",
    square: "grid", settings: "gear", scissors: "scissors",
    paintbrush: "brush", bell: "bell", wrench: "wrench",
  };
  return map[icon] || "wrench";
}
