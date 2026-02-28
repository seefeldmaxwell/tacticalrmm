/**
 * Utility helpers
 */

// Convert numeric rating to letter grade (Angie's List style)
export function letterGrade(rating: number | null): string {
  if (!rating || rating <= 0) return "N/A";
  if (rating >= 4.5) return "A";
  if (rating >= 3.5) return "B";
  if (rating >= 2.5) return "C";
  if (rating >= 1.5) return "D";
  return "F";
}

// Generate star HTML
export function starRating(rating: number | null): string {
  if (!rating) return '<span class="text-muted">No ratings</span>';
  const full = Math.floor(rating);
  const half = rating - full >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  let stars = "";
  for (let i = 0; i < full; i++) stars += "&#9733;";
  for (let i = 0; i < half; i++) stars += "&#9734;";
  for (let i = 0; i < empty; i++) stars += "&#9734;";
  return `<span class="stars text-warning">${stars}</span> <small>(${rating.toFixed(1)})</small>`;
}

// License status badge
export function statusBadge(status: string | null): string {
  if (!status) return '<span class="badge bg-secondary">Unknown</span>';
  const s = status.toLowerCase();
  if (s === "current")
    return '<span class="badge bg-success">Active</span>';
  if (s === "delinquent")
    return '<span class="badge bg-warning text-dark">Delinquent</span>';
  if (s === "suspended" || s === "null & void")
    return `<span class="badge bg-danger">${status}</span>`;
  if (s === "revoked")
    return '<span class="badge bg-danger">Revoked</span>';
  if (s.includes("inactive"))
    return '<span class="badge bg-secondary">Inactive</span>';
  return `<span class="badge bg-secondary">${status}</span>`;
}

// Legal case severity badge
export function severityBadge(severity: string): string {
  const s = severity.toLowerCase();
  if (s === "critical") return '<span class="badge bg-danger">Critical</span>';
  if (s === "high") return '<span class="badge bg-warning text-dark">High</span>';
  if (s === "medium") return '<span class="badge bg-info">Medium</span>';
  return '<span class="badge bg-secondary">Low</span>';
}

// Format currency
export function formatCurrency(amount: number | null): string {
  if (!amount) return "$0.00";
  return `$${amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

// Format date
export function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  try {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

// Urgency badge
export function urgencyBadge(urgency: string): string {
  const u = urgency.toLowerCase();
  if (u === "emergency") return '<span class="badge bg-danger">Emergency</span>';
  if (u === "high") return '<span class="badge bg-warning text-dark">High</span>';
  if (u === "normal") return '<span class="badge bg-info">Normal</span>';
  return '<span class="badge bg-secondary">Low</span>';
}

// Job status badge
export function jobStatusBadge(status: string): string {
  const s = status.toLowerCase();
  if (s === "open") return '<span class="badge bg-success">Open</span>';
  if (s === "in_progress") return '<span class="badge bg-primary">In Progress</span>';
  if (s === "completed") return '<span class="badge bg-secondary">Completed</span>';
  return '<span class="badge bg-dark">Cancelled</span>';
}

// Truncate text
export function truncate(text: string, length: number = 150): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + "...";
}
