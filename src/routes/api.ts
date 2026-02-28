/**
 * REST API routes
 */

import { Hono } from "hono";
import type { Env } from "../types";
import { lookupLicense, scrapeLicenseByNumber, saveLicense } from "../lib/scraper";

type HonoEnv = { Bindings: Env };

const api = new Hono<HonoEnv>();

// ─── License API ─────────────────────────────────────────────────────────────

api.get("/licenses", async (c) => {
  const db = c.env.DB;
  const q = c.req.query("q") || "";
  const limit = Math.min(parseInt(c.req.query("limit") || "50"), 100);

  let results;
  if (q) {
    const term = `%${q}%`;
    results = await db
      .prepare(
        `SELECT l.*, tc.name as category_name,
          (SELECT COUNT(*) FROM legal_cases WHERE license_id = l.id) as legal_case_count,
          (SELECT COUNT(*) FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id WHERE cp.license_id = l.id) as review_count,
          (SELECT AVG(r.rating) FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id WHERE cp.license_id = l.id) as avg_rating
        FROM licenses l LEFT JOIN trade_categories tc ON l.category_id = tc.id
        WHERE l.license_number LIKE ? OR l.licensee_name LIKE ?
        ORDER BY l.last_scraped DESC LIMIT ?`
      )
      .bind(term, term, limit)
      .all();
  } else {
    results = await db
      .prepare(
        `SELECT l.*, tc.name as category_name,
          (SELECT COUNT(*) FROM legal_cases WHERE license_id = l.id) as legal_case_count
        FROM licenses l LEFT JOIN trade_categories tc ON l.category_id = tc.id
        ORDER BY l.last_scraped DESC LIMIT ?`
      )
      .bind(limit)
      .all();
  }

  return c.json({ results: results.results, count: results.results?.length || 0 });
});

api.get("/licenses/:number", async (c) => {
  const licNum = c.req.param("number");
  const license = await lookupLicense(c.env, licNum);

  if (!license) {
    return c.json({ error: "License not found" }, 404);
  }

  // Get legal cases and reviews
  const [legalCases, reviews] = await Promise.all([
    c.env.DB.prepare("SELECT * FROM legal_cases WHERE license_id = ? ORDER BY filed_date DESC")
      .bind(license.id).all(),
    c.env.DB.prepare(
      `SELECT r.*, u.first_name || ' ' || u.last_name as reviewer_name
       FROM reviews r JOIN contractor_profiles cp ON r.contractor_id = cp.id
       JOIN users u ON r.user_id = u.id WHERE cp.license_id = ?`
    ).bind(license.id).all(),
  ]);

  return c.json({
    license,
    legal_cases: legalCases.results,
    reviews: reviews.results,
  });
});

// Scrape/refresh a license from DBPR
api.post("/licenses/:number/scrape", async (c) => {
  const licNum = c.req.param("number");

  const scraped = await scrapeLicenseByNumber(licNum);
  if (!scraped) {
    return c.json({ error: "Could not scrape license from DBPR" }, 404);
  }

  const prefix = licNum.replace(/[0-9]/g, "");
  const cat = await c.env.DB.prepare("SELECT id FROM trade_categories WHERE prefix = ?")
    .bind(prefix).first<{ id: number }>();

  await saveLicense(c.env.DB, scraped, cat?.id || null);

  return c.json({ message: "License scraped and saved", data: scraped });
});

// ─── Legal Cases API ─────────────────────────────────────────────────────────

api.get("/legal-cases", async (c) => {
  const db = c.env.DB;
  const licenseId = c.req.query("license_id");
  const status = c.req.query("status");

  let query = `
    SELECT lc.*, l.license_number, l.licensee_name
    FROM legal_cases lc
    JOIN licenses l ON lc.license_id = l.id
    WHERE 1=1`;
  const params: string[] = [];

  if (licenseId) { query += " AND lc.license_id = ?"; params.push(licenseId); }
  if (status) { query += " AND lc.status = ?"; params.push(status); }
  query += " ORDER BY lc.filed_date DESC LIMIT 100";

  const stmt = db.prepare(query);
  const results = params.length > 0 ? await stmt.bind(...params).all() : await stmt.all();

  return c.json({ results: results.results, count: results.results?.length || 0 });
});

// ─── Contractors API ─────────────────────────────────────────────────────────

api.get("/contractors", async (c) => {
  const db = c.env.DB;
  const trade = c.req.query("trade");

  let query = `
    SELECT cp.*, u.first_name, u.last_name, l.license_number, l.status as license_status,
      tc.name as category_name,
      (SELECT COUNT(*) FROM legal_cases WHERE license_id = cp.license_id) as legal_case_count
    FROM contractor_profiles cp
    JOIN users u ON cp.user_id = u.id
    LEFT JOIN licenses l ON cp.license_id = l.id
    LEFT JOIN trade_categories tc ON l.category_id = tc.id
    WHERE cp.is_verified = 1`;

  const params: string[] = [];
  if (trade) { query += " AND tc.slug = ?"; params.push(trade); }
  query += " ORDER BY cp.avg_rating DESC";

  const stmt = db.prepare(query);
  const results = params.length > 0 ? await stmt.bind(...params).all() : await stmt.all();

  return c.json({ results: results.results });
});

api.get("/contractors/:id", async (c) => {
  const db = c.env.DB;
  const id = c.req.param("id");

  const contractor = await db.prepare(
    `SELECT cp.*, u.first_name, u.last_name, l.license_number, l.status as license_status,
      tc.name as category_name,
      (SELECT COUNT(*) FROM legal_cases WHERE license_id = cp.license_id) as legal_case_count
    FROM contractor_profiles cp
    JOIN users u ON cp.user_id = u.id
    LEFT JOIN licenses l ON cp.license_id = l.id
    LEFT JOIN trade_categories tc ON l.category_id = tc.id
    WHERE cp.id = ?`
  ).bind(id).first();

  if (!contractor) return c.json({ error: "Not found" }, 404);

  const [reviews, legalCases] = await Promise.all([
    db.prepare("SELECT r.*, u.first_name || ' ' || u.last_name as reviewer_name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.contractor_id = ? ORDER BY r.created_at DESC")
      .bind(id).all(),
    (contractor as any).license_id
      ? db.prepare("SELECT * FROM legal_cases WHERE license_id = ? ORDER BY filed_date DESC")
          .bind((contractor as any).license_id).all()
      : Promise.resolve({ results: [] }),
  ]);

  return c.json({ contractor, reviews: reviews.results, legal_cases: (legalCases as any).results });
});

// ─── Jobs API ────────────────────────────────────────────────────────────────

api.get("/jobs", async (c) => {
  const db = c.env.DB;
  const status = c.req.query("status");

  let query = `
    SELECT j.*, tc.name as category_name,
      (SELECT COUNT(*) FROM bids WHERE job_id = j.id) as bid_count
    FROM jobs j
    LEFT JOIN trade_categories tc ON j.category_id = tc.id
    WHERE 1=1`;
  const params: string[] = [];
  if (status) { query += " AND j.status = ?"; params.push(status); }
  query += " ORDER BY j.created_at DESC";

  const stmt = db.prepare(query);
  const results = params.length > 0 ? await stmt.bind(...params).all() : await stmt.all();
  return c.json({ results: results.results });
});

api.get("/jobs/:id", async (c) => {
  const db = c.env.DB;
  const id = c.req.param("id");

  const job = await db.prepare(
    `SELECT j.*, tc.name as category_name, u.first_name || ' ' || u.last_name as poster_name
     FROM jobs j LEFT JOIN trade_categories tc ON j.category_id = tc.id
     LEFT JOIN users u ON j.user_id = u.id WHERE j.id = ?`
  ).bind(id).first();

  if (!job) return c.json({ error: "Not found" }, 404);

  const bids = await db.prepare(
    `SELECT b.*, cp.business_name, cp.avg_rating, cp.total_reviews,
      u.first_name || ' ' || u.last_name as contractor_name,
      l.license_number, l.status as license_status,
      (SELECT COUNT(*) FROM legal_cases WHERE license_id = cp.license_id) as legal_case_count
    FROM bids b JOIN contractor_profiles cp ON b.contractor_id = cp.id
    JOIN users u ON cp.user_id = u.id LEFT JOIN licenses l ON cp.license_id = l.id
    WHERE b.job_id = ?`
  ).bind(id).all();

  return c.json({ job, bids: bids.results });
});

// ─── Reviews API ─────────────────────────────────────────────────────────────

api.get("/reviews", async (c) => {
  const db = c.env.DB;
  const contractorId = c.req.query("contractor_id");

  let query = `SELECT r.*, u.first_name || ' ' || u.last_name as reviewer_name FROM reviews r JOIN users u ON r.user_id = u.id`;
  const params: string[] = [];
  if (contractorId) { query += " WHERE r.contractor_id = ?"; params.push(contractorId); }
  query += " ORDER BY r.created_at DESC LIMIT 100";

  const stmt = db.prepare(query);
  const results = params.length > 0 ? await stmt.bind(...params).all() : await stmt.all();
  return c.json({ results: results.results });
});

// ─── Trade Categories API ────────────────────────────────────────────────────

api.get("/trades", async (c) => {
  const results = await c.env.DB.prepare("SELECT * FROM trade_categories ORDER BY name").all();
  return c.json({ results: results.results });
});

export { api };
