// Cloudflare Worker Environment Bindings
export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
  APP_NAME: string;
  DBPR_BASE_URL: string;
}

// Database row types
export interface TradeCategory {
  id: number;
  name: string;
  slug: string;
  board_name: string;
  license_code: string;
  prefix: string;
  description: string;
  icon: string;
  created_at: string;
}

export interface License {
  id: number;
  license_number: string;
  licensee_name: string;
  dba_name: string | null;
  category_id: number;
  status: string;
  rank: string | null;
  license_type: string | null;
  address: string | null;
  city: string | null;
  state: string;
  zip_code: string | null;
  county: string | null;
  phone: string | null;
  email: string | null;
  issue_date: string | null;
  expiration_date: string | null;
  last_renewal_date: string | null;
  last_scraped: string;
  created_at: string;
  updated_at: string;
  // Joined fields
  category_name?: string;
  category_slug?: string;
  legal_case_count?: number;
  review_count?: number;
  avg_rating?: number;
}

export interface LegalCase {
  id: number;
  license_id: number;
  case_number: string | null;
  case_type: string;
  status: string;
  severity: string;
  title: string | null;
  description: string | null;
  filed_date: string | null;
  closed_date: string | null;
  outcome: string | null;
  fine_amount: number;
  restitution_amount: number;
  license_action: string | null;
  source_url: string | null;
  created_at: string;
  // Joined
  license_number?: string;
  licensee_name?: string;
}

export interface User {
  id: number;
  email: string;
  password_hash: string;
  first_name: string;
  last_name: string;
  role: string;
  phone: string | null;
  city: string | null;
  state: string;
  avatar_url: string | null;
  is_active: number;
  created_at: string;
}

export interface ContractorProfile {
  id: number;
  user_id: number;
  license_id: number | null;
  business_name: string | null;
  bio: string | null;
  years_experience: number;
  service_area: string | null;
  website: string | null;
  is_verified: number;
  avg_rating: number;
  total_reviews: number;
  created_at: string;
  // Joined fields
  first_name?: string;
  last_name?: string;
  email?: string;
  license_number?: string;
  license_status?: string;
  category_name?: string;
  legal_case_count?: number;
}

export interface Job {
  id: number;
  user_id: number;
  category_id: number;
  title: string;
  description: string;
  status: string;
  urgency: string;
  budget_min: number | null;
  budget_max: number | null;
  city: string | null;
  state: string;
  zip_code: string | null;
  requires_license: number;
  created_at: string;
  updated_at: string;
  // Joined
  poster_name?: string;
  category_name?: string;
  bid_count?: number;
}

export interface Bid {
  id: number;
  job_id: number;
  contractor_id: number;
  amount: number;
  message: string | null;
  estimated_days: number | null;
  status: string;
  created_at: string;
  // Joined
  business_name?: string;
  contractor_name?: string;
  license_number?: string;
  license_status?: string;
  avg_rating?: number;
  total_reviews?: number;
  legal_case_count?: number;
}

export interface Review {
  id: number;
  contractor_id: number;
  user_id: number;
  job_id: number | null;
  rating: number;
  quality_rating: number | null;
  punctuality_rating: number | null;
  price_rating: number | null;
  professionalism_rating: number | null;
  communication_rating: number | null;
  title: string | null;
  comment: string | null;
  would_recommend: number;
  created_at: string;
  // Joined
  reviewer_name?: string;
}
