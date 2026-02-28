/**
 * Florida DBPR License Scraper Engine
 * Scrapes license data from the Florida Department of Business and Professional Regulation
 */

import type { Env, License } from "../types";

// All FL skilled trade license types
export const TRADE_LICENSE_TYPES: Record<
  string,
  { name: string; board: string; code: string; prefix: string }
> = {
  electrical: {
    name: "Electrical",
    board: "Electrical Contractors Licensing Board",
    code: "ECLB",
    prefix: "EC",
  },
  plumbing: {
    name: "Plumbing",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CFC",
  },
  hvac: {
    name: "HVAC",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CAC",
  },
  "general-contractor": {
    name: "General Contractor",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CGC",
  },
  roofing: {
    name: "Roofing",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CCC",
  },
  "building-contractor": {
    name: "Building Contractor",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CBC",
  },
  "underground-utility": {
    name: "Underground Utility",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CUC",
  },
  solar: {
    name: "Solar",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CSI",
  },
  "pool-spa": {
    name: "Pool/Spa",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CPC",
  },
  mechanical: {
    name: "Mechanical",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CMC",
  },
  "sheet-metal": {
    name: "Sheet Metal",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "CSM",
  },
  painting: {
    name: "Painting",
    board: "Painting Contractors",
    code: "CILB",
    prefix: "PA",
  },
  "alarm-low-voltage": {
    name: "Alarm/Low Voltage",
    board: "Electrical Contractors Licensing Board",
    code: "ECLB",
    prefix: "EF",
  },
  "glass-glazing": {
    name: "Glass/Glazing",
    board: "Construction Industry Licensing Board",
    code: "CILB",
    prefix: "SCC",
  },
};

interface ScrapeResult {
  license_number: string;
  licensee_name: string;
  dba_name?: string;
  status: string;
  rank?: string;
  license_type?: string;
  address?: string;
  city?: string;
  county?: string;
  zip_code?: string;
  phone?: string;
  email?: string;
  issue_date?: string;
  expiration_date?: string;
}

/**
 * Scrape licenses from FL DBPR by license number
 */
export async function scrapeLicenseByNumber(
  licenseNumber: string
): Promise<ScrapeResult | null> {
  try {
    const url = `https://www.myfloridalicense.com/wl11.asp?mode=2&search=LicNbr&SID=&bession=&licid=&page=1&id=&ession=&searchterm=${encodeURIComponent(licenseNumber)}`;
    const resp = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    });

    if (!resp.ok) return null;

    const html = await resp.text();
    return parseLicenseDetailHtml(html, licenseNumber);
  } catch {
    return null;
  }
}

/**
 * Scrape licenses from FL DBPR by name
 */
export async function scrapeLicensesByName(
  name: string
): Promise<ScrapeResult[]> {
  try {
    const url = `https://www.myfloridalicense.com/wl11.asp?mode=2&search=Name&SID=&bession=&licid=&page=1&id=&ession=&searchterm=${encodeURIComponent(name)}`;
    const resp = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    });

    if (!resp.ok) return [];

    const html = await resp.text();
    return parseLicenseListHtml(html);
  } catch {
    return [];
  }
}

/**
 * Save scraped license data to D1
 */
export async function saveLicense(
  db: D1Database,
  data: ScrapeResult,
  categoryId: number | null
): Promise<void> {
  await db
    .prepare(
      `INSERT INTO licenses (license_number, licensee_name, dba_name, category_id, status, rank, license_type, address, city, county, zip_code, phone, email, issue_date, expiration_date, last_scraped)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
     ON CONFLICT(license_number) DO UPDATE SET
       licensee_name = excluded.licensee_name,
       dba_name = excluded.dba_name,
       category_id = COALESCE(excluded.category_id, licenses.category_id),
       status = excluded.status,
       rank = excluded.rank,
       license_type = excluded.license_type,
       address = excluded.address,
       city = excluded.city,
       county = excluded.county,
       zip_code = excluded.zip_code,
       phone = excluded.phone,
       email = excluded.email,
       issue_date = excluded.issue_date,
       expiration_date = excluded.expiration_date,
       last_scraped = datetime('now'),
       updated_at = datetime('now')`
    )
    .bind(
      data.license_number,
      data.licensee_name,
      data.dba_name || null,
      categoryId,
      data.status,
      data.rank || null,
      data.license_type || null,
      data.address || null,
      data.city || null,
      data.county || null,
      data.zip_code || null,
      data.phone || null,
      data.email || null,
      data.issue_date || null,
      data.expiration_date || null
    )
    .run();
}

/**
 * Look up a license, checking cache/DB first, then scraping if needed
 */
export async function lookupLicense(
  env: Env,
  licenseNumber: string
): Promise<License | null> {
  // Check KV cache first
  const cacheKey = `license:${licenseNumber}`;
  const cached = await env.CACHE.get(cacheKey, "json");
  if (cached) return cached as License;

  // Check D1
  const existing = await env.DB.prepare(
    `SELECT l.*, tc.name as category_name, tc.slug as category_slug,
      (SELECT COUNT(*) FROM legal_cases WHERE license_id = l.id) as legal_case_count
     FROM licenses l
     LEFT JOIN trade_categories tc ON l.category_id = tc.id
     WHERE l.license_number = ?`
  )
    .bind(licenseNumber)
    .first<License>();

  if (existing) {
    // Cache for 1 hour
    await env.CACHE.put(cacheKey, JSON.stringify(existing), {
      expirationTtl: 3600,
    });
    return existing;
  }

  // Scrape from DBPR
  const scraped = await scrapeLicenseByNumber(licenseNumber);
  if (!scraped) return null;

  // Determine category from prefix
  const prefix = licenseNumber.replace(/[0-9]/g, "");
  let categoryId: number | null = null;
  for (const [, info] of Object.entries(TRADE_LICENSE_TYPES)) {
    if (info.prefix === prefix) {
      const cat = await env.DB.prepare(
        "SELECT id FROM trade_categories WHERE prefix = ?"
      )
        .bind(prefix)
        .first<{ id: number }>();
      if (cat) categoryId = cat.id;
      break;
    }
  }

  await saveLicense(env.DB, scraped, categoryId);

  // Fetch the saved record
  const saved = await env.DB.prepare(
    `SELECT l.*, tc.name as category_name, tc.slug as category_slug,
      (SELECT COUNT(*) FROM legal_cases WHERE license_id = l.id) as legal_case_count
     FROM licenses l
     LEFT JOIN trade_categories tc ON l.category_id = tc.id
     WHERE l.license_number = ?`
  )
    .bind(licenseNumber)
    .first<License>();

  if (saved) {
    await env.CACHE.put(cacheKey, JSON.stringify(saved), {
      expirationTtl: 3600,
    });
  }

  return saved;
}

// HTML parsing helpers - extract data from DBPR response
function parseLicenseDetailHtml(
  html: string,
  licenseNumber: string
): ScrapeResult | null {
  // Extract key fields using regex patterns from the DBPR HTML structure
  const nameMatch = html.match(
    /Licensee Name[^<]*<[^>]*>([^<]+)/i
  );
  const statusMatch = html.match(
    /License Status[^<]*<[^>]*>([^<]+)/i
  );
  const cityMatch = html.match(/City[^<]*<[^>]*>([^<]+)/i);
  const countyMatch = html.match(/County[^<]*<[^>]*>([^<]+)/i);
  const expirationMatch = html.match(
    /Expir[^<]*<[^>]*>([^<]+)/i
  );
  const rankMatch = html.match(/Rank[^<]*<[^>]*>([^<]+)/i);

  if (!nameMatch) return null;

  return {
    license_number: licenseNumber,
    licensee_name: nameMatch[1].trim(),
    status: statusMatch ? statusMatch[1].trim() : "Unknown",
    city: cityMatch ? cityMatch[1].trim() : undefined,
    county: countyMatch ? countyMatch[1].trim() : undefined,
    expiration_date: expirationMatch ? expirationMatch[1].trim() : undefined,
    rank: rankMatch ? rankMatch[1].trim() : undefined,
  };
}

function parseLicenseListHtml(html: string): ScrapeResult[] {
  const results: ScrapeResult[] = [];
  // Match table rows containing license data
  const rowPattern =
    /<tr[^>]*>[\s\S]*?<td[^>]*>([\w]+\d+)<\/td>[\s\S]*?<td[^>]*>([^<]+)<\/td>[\s\S]*?<td[^>]*>([^<]+)<\/td>/gi;
  let match;

  while ((match = rowPattern.exec(html)) !== null) {
    results.push({
      license_number: match[1].trim(),
      licensee_name: match[2].trim(),
      status: match[3].trim(),
    });
  }

  return results;
}
