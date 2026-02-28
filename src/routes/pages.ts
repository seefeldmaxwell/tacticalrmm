/**
 * Page routes - serves HTML pages
 */

import { Hono } from "hono";
import type { Env } from "../types";
import { homePage } from "../templates/home";
import { searchPage } from "../templates/search";
import { licenseDetailPage } from "../templates/license-detail";
import { contractorListPage, contractorDetailPage } from "../templates/contractors";
import { jobListPage, jobDetailPage } from "../templates/jobs";
import { tradeListPage, tradeDetailPage } from "../templates/trades";

type HonoEnv = { Bindings: Env };

const pages = new Hono<HonoEnv>();

// ─── Home ────────────────────────────────────────────────────────────────────

pages.get("/", async (c) => {
  const db = c.env.DB;

  const [licensesCount, contractorsCount, jobsCount, categories, featured] =
    await Promise.all([
      db.prepare("SELECT COUNT(*) as cnt FROM licenses").first<{ cnt: number }>(),
      db.prepare("SELECT COUNT(*) as cnt FROM contractor_profiles WHERE is_verified = 1").first<{ cnt: number }>(),
      db.prepare("SELECT COUNT(*) as cnt FROM jobs WHERE status = 'open'").first<{ cnt: number }>(),
      db.prepare("SELECT * FROM trade_categories ORDER BY name").all(),
      db.prepare(`
        SELECT cp.*, u.first_name, u.last_name, l.license_number, l.status as license_status,
          tc.name as category_name,
          (SELECT COUNT(*) FROM legal_cases WHERE license_id = cp.license_id) as legal_case_count
        FROM contractor_profiles cp
        JOIN users u ON cp.user_id = u.id
        LEFT JOIN licenses l ON cp.license_id = l.id
        LEFT JOIN trade_categories tc ON l.category_id = tc.id
        WHERE cp.is_verified = 1
        ORDER BY cp.avg_rating DESC LIMIT 6
      `).all(),
    ]);

  return c.html(
    homePage(
      {
        licenses: licensesCount?.cnt || 0,
        contractors: contractorsCount?.cnt || 0,
        jobs: jobsCount?.cnt || 0,
        trades: categories.results?.length || 0,
      },
      featured.results as any[],
      categories.results as any[]
    )
  );
});

// ─── License Search ──────────────────────────────────────────────────────────

pages.get("/search", async (c) => {
  const db = c.env.DB;
  const query = c.req.query("q") || "";

  let results: any[] = [];
  if (query) {
    const term = `%${query}%`;
    const res = await db
      .prepare(
        `SELECT l.*, tc.name as category_name, tc.slug as category_slug,
          (SELECT COUNT(*) FROM legal_cases WHERE license_id = l.id) as legal_case_count,
          (SELECT COUNT(*) FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id WHERE cp.license_id = l.id) as review_count,
          (SELECT AVG(r.rating) FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id WHERE cp.license_id = l.id) as avg_rating
        FROM licenses l
        LEFT JOIN trade_categories tc ON l.category_id = tc.id
        WHERE l.license_number LIKE ? OR l.licensee_name LIKE ? OR l.dba_name LIKE ? OR l.county LIKE ?
        ORDER BY l.last_scraped DESC LIMIT 100`
      )
      .bind(term, term, term, term)
      .all();
    results = res.results || [];
  }

  return c.html(searchPage(query, results));
});

// ─── License Detail ──────────────────────────────────────────────────────────

pages.get("/licenses/:number", async (c) => {
  const db = c.env.DB;
  const licNum = c.req.param("number");

  const license = await db
    .prepare(
      `SELECT l.*, tc.name as category_name, tc.slug as category_slug
       FROM licenses l
       LEFT JOIN trade_categories tc ON l.category_id = tc.id
       WHERE l.license_number = ?`
    )
    .bind(licNum)
    .first();

  if (!license) {
    return c.html(
      `<div class="container mt-4"><div class="alert alert-warning">License ${licNum} not found. <a href="/search?q=${licNum}">Try searching</a></div></div>`,
      404
    );
  }

  const [legalCases, reviews, contractor] = await Promise.all([
    db.prepare("SELECT * FROM legal_cases WHERE license_id = ? ORDER BY filed_date DESC")
      .bind(license.id)
      .all(),
    db.prepare(
      `SELECT r.*, u.first_name || ' ' || u.last_name as reviewer_name
       FROM reviews r
       JOIN contractor_profiles cp ON r.contractor_id = cp.id
       JOIN users u ON r.user_id = u.id
       WHERE cp.license_id = ?
       ORDER BY r.created_at DESC`
    )
      .bind(license.id)
      .all(),
    db.prepare(
      `SELECT cp.*, u.first_name, u.last_name, l.license_number, l.status as license_status
       FROM contractor_profiles cp
       JOIN users u ON cp.user_id = u.id
       LEFT JOIN licenses l ON cp.license_id = l.id
       WHERE cp.license_id = ?`
    )
      .bind(license.id)
      .first(),
  ]);

  return c.html(
    licenseDetailPage(
      license as any,
      (legalCases.results || []) as any[],
      (reviews.results || []) as any[],
      contractor as any
    )
  );
});

// ─── Contractors ─────────────────────────────────────────────────────────────

pages.get("/contractors", async (c) => {
  const db = c.env.DB;
  const trade = c.req.query("trade") || "";

  let query = `
    SELECT cp.*, u.first_name, u.last_name, l.license_number, l.status as license_status,
      tc.name as category_name, tc.slug as category_slug,
      (SELECT COUNT(*) FROM legal_cases WHERE license_id = cp.license_id) as legal_case_count
    FROM contractor_profiles cp
    JOIN users u ON cp.user_id = u.id
    LEFT JOIN licenses l ON cp.license_id = l.id
    LEFT JOIN trade_categories tc ON l.category_id = tc.id
    WHERE cp.is_verified = 1`;

  const params: string[] = [];
  if (trade) {
    query += " AND tc.slug = ?";
    params.push(trade);
  }
  query += " ORDER BY cp.avg_rating DESC";

  const stmt = db.prepare(query);
  const contractors = params.length > 0 ? await stmt.bind(...params).all() : await stmt.all();

  const categories = await db.prepare("SELECT * FROM trade_categories ORDER BY name").all();

  return c.html(contractorListPage(
    (contractors.results || []) as any[],
    (categories.results || []) as any[],
    trade
  ));
});

pages.get("/contractors/:id", async (c) => {
  const db = c.env.DB;
  const id = c.req.param("id");

  const contractor = await db
    .prepare(
      `SELECT cp.*, u.first_name, u.last_name, u.email, l.license_number, l.status as license_status,
        tc.name as category_name
       FROM contractor_profiles cp
       JOIN users u ON cp.user_id = u.id
       LEFT JOIN licenses l ON cp.license_id = l.id
       LEFT JOIN trade_categories tc ON l.category_id = tc.id
       WHERE cp.id = ?`
    )
    .bind(id)
    .first();

  if (!contractor) {
    return c.html('<div class="container mt-4"><div class="alert alert-warning">Contractor not found.</div></div>', 404);
  }

  const [reviews, legalCases] = await Promise.all([
    db.prepare(
      `SELECT r.*, u.first_name || ' ' || u.last_name as reviewer_name
       FROM reviews r
       JOIN users u ON r.user_id = u.id
       WHERE r.contractor_id = ?
       ORDER BY r.created_at DESC`
    )
      .bind(id)
      .all(),
    contractor.license_id
      ? db.prepare("SELECT * FROM legal_cases WHERE license_id = ? ORDER BY filed_date DESC")
          .bind(contractor.license_id)
          .all()
      : Promise.resolve({ results: [] }),
  ]);

  return c.html(
    contractorDetailPage(
      contractor as any,
      (reviews.results || []) as any[],
      ((legalCases as any).results || []) as any[]
    )
  );
});

// ─── Jobs ────────────────────────────────────────────────────────────────────

pages.get("/jobs", async (c) => {
  const db = c.env.DB;
  const trade = c.req.query("trade") || "";
  const status = c.req.query("status") || "";

  let query = `
    SELECT j.*, tc.name as category_name, u.first_name || ' ' || u.last_name as poster_name,
      (SELECT COUNT(*) FROM bids WHERE job_id = j.id) as bid_count
    FROM jobs j
    LEFT JOIN trade_categories tc ON j.category_id = tc.id
    LEFT JOIN users u ON j.user_id = u.id
    WHERE 1=1`;

  const params: string[] = [];
  if (trade) {
    query += " AND tc.slug = ?";
    params.push(trade);
  }
  if (status) {
    query += " AND j.status = ?";
    params.push(status);
  }
  query += " ORDER BY j.created_at DESC";

  const stmt = db.prepare(query);
  const jobs = params.length > 0 ? await stmt.bind(...params).all() : await stmt.all();
  const categories = await db.prepare("SELECT * FROM trade_categories ORDER BY name").all();

  return c.html(jobListPage(
    (jobs.results || []) as any[],
    (categories.results || []) as any[],
    trade,
    status
  ));
});

pages.get("/jobs/:id", async (c) => {
  const db = c.env.DB;
  const id = c.req.param("id");

  const job = await db
    .prepare(
      `SELECT j.*, tc.name as category_name, u.first_name || ' ' || u.last_name as poster_name
       FROM jobs j
       LEFT JOIN trade_categories tc ON j.category_id = tc.id
       LEFT JOIN users u ON j.user_id = u.id
       WHERE j.id = ?`
    )
    .bind(id)
    .first();

  if (!job) {
    return c.html('<div class="container mt-4"><div class="alert alert-warning">Job not found.</div></div>', 404);
  }

  const bids = await db
    .prepare(
      `SELECT b.*, cp.business_name, cp.avg_rating, cp.total_reviews,
        u.first_name || ' ' || u.last_name as contractor_name,
        l.license_number, l.status as license_status,
        (SELECT COUNT(*) FROM legal_cases WHERE license_id = cp.license_id) as legal_case_count
       FROM bids b
       JOIN contractor_profiles cp ON b.contractor_id = cp.id
       JOIN users u ON cp.user_id = u.id
       LEFT JOIN licenses l ON cp.license_id = l.id
       WHERE b.job_id = ?
       ORDER BY b.created_at DESC`
    )
    .bind(id)
    .all();

  return c.html(jobDetailPage(job as any, (bids.results || []) as any[]));
});

// ─── Trade Categories ────────────────────────────────────────────────────────

pages.get("/trades", async (c) => {
  const db = c.env.DB;
  const categories = await db.prepare("SELECT * FROM trade_categories ORDER BY name").all();
  return c.html(tradeListPage((categories.results || []) as any[]));
});

pages.get("/trades/:slug", async (c) => {
  const db = c.env.DB;
  const slug = c.req.param("slug");

  const category = await db
    .prepare("SELECT * FROM trade_categories WHERE slug = ?")
    .bind(slug)
    .first();

  if (!category) {
    return c.html('<div class="container mt-4"><div class="alert alert-warning">Trade category not found.</div></div>', 404);
  }

  const licenses = await db
    .prepare(
      `SELECT l.*,
        (SELECT COUNT(*) FROM legal_cases WHERE license_id = l.id) as legal_case_count,
        (SELECT COUNT(*) FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id WHERE cp.license_id = l.id) as review_count,
        (SELECT AVG(r.rating) FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id WHERE cp.license_id = l.id) as avg_rating
       FROM licenses l
       WHERE l.category_id = ?
       ORDER BY l.licensee_name`
    )
    .bind(category.id)
    .all();

  return c.html(tradeDetailPage(category as any, (licenses.results || []) as any[]));
});

export { pages };
