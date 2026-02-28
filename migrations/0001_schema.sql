-- FL License Scraper & Job Board Schema

-- Trade categories (Electrical, Plumbing, HVAC, etc.)
CREATE TABLE IF NOT EXISTS trade_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  board_name TEXT,
  license_code TEXT,
  prefix TEXT,
  description TEXT,
  icon TEXT DEFAULT 'wrench',
  created_at TEXT DEFAULT (datetime('now'))
);

-- Florida DBPR Licenses
CREATE TABLE IF NOT EXISTS licenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  license_number TEXT NOT NULL UNIQUE,
  licensee_name TEXT NOT NULL,
  dba_name TEXT,
  category_id INTEGER REFERENCES trade_categories(id),
  status TEXT NOT NULL DEFAULT 'Unknown',
  -- Current, Delinquent, Null & Void, Suspended, Revoked, Voluntarily Inactive
  rank TEXT,
  license_type TEXT,
  address TEXT,
  city TEXT,
  state TEXT DEFAULT 'FL',
  zip_code TEXT,
  county TEXT,
  phone TEXT,
  email TEXT,
  issue_date TEXT,
  expiration_date TEXT,
  last_renewal_date TEXT,
  last_scraped TEXT DEFAULT (datetime('now')),
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_licenses_number ON licenses(license_number);
CREATE INDEX IF NOT EXISTS idx_licenses_name ON licenses(licensee_name);
CREATE INDEX IF NOT EXISTS idx_licenses_category ON licenses(category_id);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
CREATE INDEX IF NOT EXISTS idx_licenses_county ON licenses(county);

-- Legal cases / disciplinary actions
CREATE TABLE IF NOT EXISTS legal_cases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  license_id INTEGER NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
  case_number TEXT,
  case_type TEXT NOT NULL DEFAULT 'Disciplinary',
  -- Disciplinary, Complaint, Violation, Administrative, Criminal, Civil, Fraud, Negligence
  status TEXT NOT NULL DEFAULT 'Open',
  -- Open, Closed, Settled, Dismissed, Pending, Under Investigation, Appeal
  severity TEXT DEFAULT 'Medium',
  -- Low, Medium, High, Critical
  title TEXT,
  description TEXT,
  filed_date TEXT,
  closed_date TEXT,
  outcome TEXT,
  fine_amount REAL DEFAULT 0,
  restitution_amount REAL DEFAULT 0,
  license_action TEXT,
  -- None, Warning, Probation, Suspension, Revocation, Voluntary Surrender
  source_url TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_legal_license ON legal_cases(license_id);
CREATE INDEX IF NOT EXISTS idx_legal_status ON legal_cases(status);
CREATE INDEX IF NOT EXISTS idx_legal_type ON legal_cases(case_type);

-- Users
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'homeowner',
  -- homeowner, contractor, admin
  phone TEXT,
  city TEXT,
  state TEXT DEFAULT 'FL',
  avatar_url TEXT,
  is_active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Contractor profiles (linked to user and license)
CREATE TABLE IF NOT EXISTS contractor_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  license_id INTEGER REFERENCES licenses(id),
  business_name TEXT,
  bio TEXT,
  years_experience INTEGER DEFAULT 0,
  service_area TEXT,
  website TEXT,
  is_verified INTEGER DEFAULT 0,
  avg_rating REAL DEFAULT 0,
  total_reviews INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_contractor_user ON contractor_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_contractor_license ON contractor_profiles(license_id);

-- Jobs posted by homeowners
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  category_id INTEGER REFERENCES trade_categories(id),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open',
  -- open, in_progress, completed, cancelled
  urgency TEXT DEFAULT 'normal',
  -- low, normal, high, emergency
  budget_min REAL,
  budget_max REAL,
  city TEXT,
  state TEXT DEFAULT 'FL',
  zip_code TEXT,
  requires_license INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_jobs_user ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);

-- Bids from contractors on jobs
CREATE TABLE IF NOT EXISTS bids (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  contractor_id INTEGER NOT NULL REFERENCES contractor_profiles(id),
  amount REAL NOT NULL,
  message TEXT,
  estimated_days INTEGER,
  status TEXT NOT NULL DEFAULT 'pending',
  -- pending, accepted, rejected, withdrawn
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_bids_job ON bids(job_id);
CREATE INDEX IF NOT EXISTS idx_bids_contractor ON bids(contractor_id);

-- Reviews
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contractor_id INTEGER NOT NULL REFERENCES contractor_profiles(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES users(id),
  job_id INTEGER REFERENCES jobs(id),
  rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
  quality_rating INTEGER CHECK(quality_rating >= 1 AND quality_rating <= 5),
  punctuality_rating INTEGER CHECK(punctuality_rating >= 1 AND punctuality_rating <= 5),
  price_rating INTEGER CHECK(price_rating >= 1 AND price_rating <= 5),
  professionalism_rating INTEGER CHECK(professionalism_rating >= 1 AND professionalism_rating <= 5),
  communication_rating INTEGER CHECK(communication_rating >= 1 AND communication_rating <= 5),
  title TEXT,
  comment TEXT,
  would_recommend INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reviews_contractor ON reviews(contractor_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);

-- Scrape log
CREATE TABLE IF NOT EXISTS scrape_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trade TEXT,
  license_number TEXT,
  records_found INTEGER DEFAULT 0,
  records_saved INTEGER DEFAULT 0,
  status TEXT DEFAULT 'running',
  error_message TEXT,
  started_at TEXT DEFAULT (datetime('now')),
  completed_at TEXT
);
