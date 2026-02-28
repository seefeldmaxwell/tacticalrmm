-- Seed trade categories from FL DBPR
INSERT OR IGNORE INTO trade_categories (name, slug, board_name, license_code, prefix, description, icon) VALUES
  ('Electrical', 'electrical', 'Electrical Contractors Licensing Board', 'ECLB', 'EC', 'Licensed electricians and electrical contractors', 'zap'),
  ('Plumbing', 'plumbing', 'Construction Industry Licensing Board', 'CILB', 'CFC', 'Licensed plumbers and plumbing contractors', 'droplet'),
  ('HVAC', 'hvac', 'Construction Industry Licensing Board', 'CILB', 'CAC', 'Heating, ventilation, and air conditioning contractors', 'thermometer'),
  ('General Contractor', 'general-contractor', 'Construction Industry Licensing Board', 'CILB', 'CGC', 'Certified general contractors', 'hard-hat'),
  ('Roofing', 'roofing', 'Construction Industry Licensing Board', 'CILB', 'CCC', 'Certified roofing contractors', 'home'),
  ('Building Contractor', 'building-contractor', 'Construction Industry Licensing Board', 'CILB', 'CBC', 'Certified building contractors', 'building'),
  ('Underground Utility', 'underground-utility', 'Construction Industry Licensing Board', 'CILB', 'CUC', 'Underground utility and excavation contractors', 'layers'),
  ('Solar', 'solar', 'Construction Industry Licensing Board', 'CILB', 'CSI', 'Solar energy system contractors', 'sun'),
  ('Pool/Spa', 'pool-spa', 'Construction Industry Licensing Board', 'CILB', 'CPC', 'Swimming pool and spa contractors', 'waves'),
  ('Pollutant Storage', 'pollutant-storage', 'Construction Industry Licensing Board', 'CILB', 'PCC', 'Pollutant storage systems contractors', 'shield'),
  ('Glass/Glazing', 'glass-glazing', 'Construction Industry Licensing Board', 'CILB', 'SCC', 'Specialty glass and glazing contractors', 'square'),
  ('Mechanical', 'mechanical', 'Construction Industry Licensing Board', 'CILB', 'CMC', 'Mechanical contractors', 'settings'),
  ('Sheet Metal', 'sheet-metal', 'Construction Industry Licensing Board', 'CILB', 'CSM', 'Sheet metal contractors', 'scissors'),
  ('Painting', 'painting', 'Painting Contractors', 'CILB', 'PA', 'Painting contractors', 'paintbrush'),
  ('Alarm/Low Voltage', 'alarm-low-voltage', 'Electrical Contractors Licensing Board', 'ECLB', 'EF', 'Alarm system and low voltage contractors', 'bell');

-- Demo data: sample users
INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, role, city) VALUES
  ('admin@flscraper.com', '$2b$10$placeholder', 'Admin', 'User', 'admin', 'Tallahassee'),
  ('john@example.com', '$2b$10$placeholder', 'John', 'Smith', 'homeowner', 'Miami'),
  ('mike@electricpro.com', '$2b$10$placeholder', 'Mike', 'Johnson', 'contractor', 'Orlando'),
  ('sarah@coolairhvac.com', '$2b$10$placeholder', 'Sarah', 'Williams', 'contractor', 'Tampa'),
  ('bob@plumbright.com', '$2b$10$placeholder', 'Bob', 'Davis', 'contractor', 'Jacksonville');

-- Demo licenses
INSERT OR IGNORE INTO licenses (license_number, licensee_name, category_id, status, city, county, issue_date, expiration_date) VALUES
  ('EC13012345', 'Mike Johnson Electric Pro LLC', 1, 'Current', 'Orlando', 'Orange', '2018-03-15', '2026-08-31'),
  ('CAC1820001', 'Sarah Williams Cool Air HVAC Inc', 3, 'Current', 'Tampa', 'Hillsborough', '2019-06-01', '2026-12-31'),
  ('CFC1430001', 'Bob Davis PlumbRight Services', 2, 'Current', 'Jacksonville', 'Duval', '2017-01-10', '2025-06-30'),
  ('CGC1525001', 'Demo General Contractor LLC', 4, 'Delinquent', 'Miami', 'Miami-Dade', '2015-09-20', '2024-03-31'),
  ('CCC1330001', 'TopRoof Contractors Inc', 5, 'Current', 'Fort Lauderdale', 'Broward', '2020-02-14', '2026-10-31');

-- Link contractors to licenses
INSERT OR IGNORE INTO contractor_profiles (user_id, license_id, business_name, bio, years_experience, service_area, is_verified, avg_rating, total_reviews) VALUES
  (3, 1, 'Electric Pro LLC', 'Licensed master electrician serving Central Florida for 15+ years. Residential and commercial.', 15, 'Orlando, Kissimmee, Winter Park', 1, 4.7, 23),
  (4, 2, 'Cool Air HVAC Inc', 'Full-service HVAC company. Installation, repair, and maintenance of all cooling and heating systems.', 10, 'Tampa, St. Petersburg, Clearwater', 1, 4.5, 18),
  (5, 3, 'PlumbRight Services', 'Expert plumbing solutions. Emergency service available 24/7. Licensed and insured.', 20, 'Jacksonville, Orange Park, St. Augustine', 1, 4.2, 31);

-- Demo legal cases
INSERT OR IGNORE INTO legal_cases (license_id, case_number, case_type, status, severity, title, description, filed_date, fine_amount, license_action) VALUES
  (4, 'DBPR-2023-04521', 'Disciplinary', 'Closed', 'High', 'Unlicensed Activity Complaint', 'Operating with a delinquent license; failure to maintain proper insurance coverage.', '2023-06-15', 2500.00, 'Probation'),
  (4, 'DBPR-2024-00891', 'Complaint', 'Open', 'Medium', 'Consumer Complaint - Incomplete Work', 'Homeowner reported contractor abandoned project before completion.', '2024-01-20', 0, 'None'),
  (3, 'DBPR-2022-08321', 'Violation', 'Closed', 'Low', 'Late Renewal Notice', 'License was renewed 30 days past expiration. No consumer harm.', '2022-11-05', 250.00, 'Warning');

-- Demo jobs
INSERT OR IGNORE INTO jobs (user_id, category_id, title, description, status, urgency, budget_min, budget_max, city, zip_code) VALUES
  (2, 1, 'Whole House Rewiring', 'Need complete rewiring of 1960s ranch home. 2,200 sq ft, current 100amp panel needs upgrade to 200amp.', 'open', 'normal', 8000, 15000, 'Miami', '33125'),
  (2, 3, 'AC Unit Replacement', 'Replace 15-year-old 3-ton AC unit. Prefer high-efficiency model. House is 1,800 sq ft.', 'open', 'high', 4000, 7000, 'Miami', '33125'),
  (2, 2, 'Bathroom Remodel Plumbing', 'Complete plumbing for master bath remodel. Moving shower, adding dual vanity.', 'in_progress', 'normal', 3000, 6000, 'Miami', '33125');

-- Demo bids
INSERT OR IGNORE INTO bids (job_id, contractor_id, amount, message, estimated_days, status) VALUES
  (1, 1, 11500, 'I can handle the full rewiring including panel upgrade. 15 years experience with older homes.', 7, 'pending'),
  (2, 2, 5200, 'Can install a Carrier Infinity 20 SEER2 unit. Includes 10-year warranty.', 2, 'pending'),
  (3, 3, 4500, 'Full bathroom plumbing relocation and new fixture installation. Licensed and insured.', 5, 'accepted');

-- Demo reviews
INSERT OR IGNORE INTO reviews (contractor_id, user_id, rating, quality_rating, punctuality_rating, price_rating, professionalism_rating, communication_rating, title, comment, would_recommend) VALUES
  (1, 2, 5, 5, 5, 4, 5, 5, 'Excellent Electrical Work', 'Mike rewired our kitchen and added a sub-panel. Clean work, on time, very professional. Highly recommend!', 1),
  (1, 2, 4, 4, 4, 4, 5, 4, 'Panel Upgrade', 'Good job upgrading from 100A to 200A panel. Passed inspection first try.', 1),
  (2, 2, 5, 5, 4, 4, 5, 5, 'New AC Install', 'Sarah and team installed new Trane system. House has never been cooler. Great follow-up service.', 1),
  (3, 2, 4, 4, 3, 4, 4, 4, 'Fixed Leak Quickly', 'Bob came out same day for emergency leak. Fixed it fast. Fair price.', 1);
