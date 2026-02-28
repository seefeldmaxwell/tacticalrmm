import { layout } from "./layout";
import type { License } from "../types";
import { statusBadge, starRating, formatDate } from "../lib/helpers";

export function searchPage(query: string, results: License[]): string {
  const resultRows = results
    .map(
      (l) => `
    <tr>
      <td><a href="/licenses/${l.license_number}"><strong>${l.license_number}</strong></a></td>
      <td>${l.licensee_name}</td>
      <td>${l.category_name || "—"}</td>
      <td>${statusBadge(l.status)}</td>
      <td>${l.city || "—"}, ${l.county || ""}</td>
      <td>${starRating(l.avg_rating || null)} ${l.review_count ? `<small>(${l.review_count})</small>` : ""}</td>
      <td>${legalCol(l.legal_case_count || 0, l.license_number)}</td>
      <td><small>${formatDate(l.expiration_date || null)}</small></td>
    </tr>`
    )
    .join("");

  return layout(
    "License Search",
    `
    <div class="hero py-4">
      <div class="container">
        <h2 class="mb-3">License Search</h2>
        <div class="search-box">
          <form action="/search" method="get">
            <div class="input-group">
              <input type="text" class="form-control" name="q" value="${escHtml(query)}" placeholder="License number, name, or trade...">
              <button class="btn btn-warning" type="submit"><i class="bi bi-search"></i> Search</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div class="container mt-4">
      ${
        query
          ? `<p class="text-muted">${results.length} result${results.length !== 1 ? "s" : ""} for "<strong>${escHtml(query)}</strong>"</p>`
          : '<p class="text-muted">Enter a license number, contractor name, or trade to search.</p>'
      }
      ${
        results.length > 0
          ? `
      <div class="table-responsive">
        <table class="table table-hover bg-white rounded">
          <thead class="table-light">
            <tr>
              <th>License #</th>
              <th>Name</th>
              <th>Trade</th>
              <th>Status</th>
              <th>Location</th>
              <th>Reviews</th>
              <th>Legal Cases</th>
              <th>Expires</th>
            </tr>
          </thead>
          <tbody>${resultRows}</tbody>
        </table>
      </div>`
          : query
            ? '<div class="alert alert-info">No results found. Try a different search term or check the license number format.</div>'
            : ""
      }
      <div class="card mt-4">
        <div class="card-body">
          <h5>Search Tips</h5>
          <ul class="mb-0">
            <li><strong>By license number:</strong> Enter the full number (e.g., EC13012345, CFC1430001)</li>
            <li><strong>By name:</strong> Enter contractor or business name</li>
            <li><strong>License prefixes:</strong> EC (Electrical), CFC (Plumbing), CAC (HVAC), CGC (General), CCC (Roofing), CBC (Building)</li>
          </ul>
        </div>
      </div>
    </div>`,
    "search"
  );
}

function legalCol(count: number, licNum: string): string {
  if (count > 0)
    return `<a href="/licenses/${licNum}#legal" class="text-danger text-decoration-none"><i class="bi bi-exclamation-triangle"></i> ${count} case${count > 1 ? "s" : ""}</a>`;
  return '<span class="text-success"><i class="bi bi-check-circle"></i> Clean</span>';
}

function escHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
