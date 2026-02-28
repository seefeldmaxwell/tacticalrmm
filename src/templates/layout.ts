/**
 * Base HTML layout template
 */

export function layout(title: string, content: string, activeNav: string = ""): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} - FL License Scraper</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <style>
    :root { --fl-blue: #003366; --fl-gold: #c4a000; }
    body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f6fa; }
    .navbar { background: var(--fl-blue) !important; }
    .navbar-brand { font-weight: 700; letter-spacing: 1px; }
    .hero { background: linear-gradient(135deg, #003366 0%, #004a8f 100%); color: white; padding: 3rem 0; }
    .card { border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
    .stars { color: #f5a623; font-size: 1.1em; }
    .grade-badge { width: 48px; height: 48px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.4rem; color: white; }
    .grade-A { background: #28a745; }
    .grade-B { background: #5cb85c; }
    .grade-C { background: #f0ad4e; }
    .grade-D { background: #d9534f; }
    .grade-F { background: #c9302c; }
    .grade-NA { background: #6c757d; }
    .legal-warning { border-left: 4px solid #dc3545; background: #fff5f5; }
    .legal-clean { border-left: 4px solid #28a745; background: #f0fff4; }
    .status-active { color: #28a745; font-weight: 600; }
    .status-delinquent { color: #f0ad4e; font-weight: 600; }
    .status-revoked, .status-suspended { color: #dc3545; font-weight: 600; }
    footer { background: var(--fl-blue); color: rgba(255,255,255,0.7); padding: 2rem 0; margin-top: 3rem; }
    footer a { color: rgba(255,255,255,0.9); }
    .search-box { max-width: 600px; margin: 0 auto; }
    .stat-card { text-align: center; padding: 1.5rem; }
    .stat-card h3 { font-size: 2rem; font-weight: 700; color: var(--fl-blue); }
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark">
    <div class="container">
      <a class="navbar-brand" href="/"><i class="bi bi-shield-check"></i> FL License Scraper</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="nav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item"><a class="nav-link ${activeNav === "home" ? "active" : ""}" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link ${activeNav === "search" ? "active" : ""}" href="/search">License Search</a></li>
          <li class="nav-item"><a class="nav-link ${activeNav === "contractors" ? "active" : ""}" href="/contractors">Contractors</a></li>
          <li class="nav-item"><a class="nav-link ${activeNav === "jobs" ? "active" : ""}" href="/jobs">Job Board</a></li>
          <li class="nav-item"><a class="nav-link ${activeNav === "trades" ? "active" : ""}" href="/trades">Trade Categories</a></li>
        </ul>
        <form class="d-flex" action="/search" method="get">
          <input class="form-control form-control-sm me-2" type="search" name="q" placeholder="License # or name...">
          <button class="btn btn-outline-light btn-sm" type="submit">Search</button>
        </form>
      </div>
    </div>
  </nav>

  <main>
    ${content}
  </main>

  <footer>
    <div class="container text-center">
      <p class="mb-1"><strong>FL License Scraper & Job Board</strong></p>
      <p class="mb-1">Data sourced from <a href="https://www.myfloridalicense.com" target="_blank">Florida DBPR</a></p>
      <p class="mb-0"><small>Verify all license information directly with the Florida Department of Business and Professional Regulation.</small></p>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>`;
}
