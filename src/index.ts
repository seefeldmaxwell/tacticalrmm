/**
 * FL License Scraper & Job Board
 * Cloudflare Worker entry point
 *
 * A Florida DBPR license scraper with Angie's List-style job board.
 * Every tradesperson listing shows: license status, legal cases, and reviews.
 */

import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import type { Env } from "./types";
import { pages } from "./routes/pages";
import { api } from "./routes/api";

type HonoEnv = { Bindings: Env };

const app = new Hono<HonoEnv>();

// Middleware
app.use("*", logger());
app.use("/api/*", cors());

// Mount page routes (HTML)
app.route("/", pages);

// Mount API routes (JSON)
app.route("/api", api);

// 404 handler
app.notFound((c) => {
  const isApi = c.req.path.startsWith("/api");
  if (isApi) {
    return c.json({ error: "Not found" }, 404);
  }
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>404 - Not Found</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
      <div class="container mt-5 text-center">
        <h1 class="display-1 text-muted">404</h1>
        <p class="lead">Page not found</p>
        <a href="/" class="btn btn-primary">Go Home</a>
      </div>
    </body>
    </html>
  `, 404);
});

// Error handler
app.onError((err, c) => {
  console.error("Error:", err);
  const isApi = c.req.path.startsWith("/api");
  if (isApi) {
    return c.json({ error: "Internal server error" }, 500);
  }
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>Error</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
      <div class="container mt-5 text-center">
        <h1 class="display-1 text-danger">Error</h1>
        <p class="lead">Something went wrong. Please try again.</p>
        <a href="/" class="btn btn-primary">Go Home</a>
      </div>
    </body>
    </html>
  `, 500);
});

// Cron trigger for scheduled scraping
export default {
  fetch: app.fetch,

  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    console.log("Cron trigger fired:", event.cron);
    // Refresh licenses that haven't been scraped in 7+ days
    const stale = await env.DB.prepare(
      `SELECT license_number FROM licenses
       WHERE last_scraped < datetime('now', '-7 days')
       ORDER BY last_scraped ASC LIMIT 20`
    ).all();

    for (const row of stale.results || []) {
      const licNum = (row as any).license_number;
      try {
        const resp = await fetch(
          `https://www.myfloridalicense.com/wl11.asp?mode=2&search=LicNbr&SID=&bession=&licid=&page=1&searchterm=${encodeURIComponent(licNum)}`,
          { headers: { "User-Agent": "Mozilla/5.0" } }
        );
        if (resp.ok) {
          await env.DB.prepare(
            "UPDATE licenses SET last_scraped = datetime('now') WHERE license_number = ?"
          ).bind(licNum).run();
        }
      } catch (e) {
        console.error(`Failed to refresh ${licNum}:`, e);
      }
    }
  },
};
