-- ============================================================
-- Tantric AI Agent — LOCAL SQLite store (development)
-- ============================================================
-- Used when DB_BACKEND=sqlite in .env (e.g. while the Oracle Cloud
-- tunnel is unreliable). Mirrors the MySQL schema in SQLite dialect.
-- Apply with:  python3 scripts/init_local_db.py
-- Idempotent: safe to re-run (CREATE IF NOT EXISTS everywhere).
--
-- Note: SQLite ignores MySQL ENUM/TIMESTAMP modifiers; TEXT/INTEGER
-- types with DEFAULT CURRENT_TIMESTAMP keep the same column names so
-- the same Python queries work on both stores.
-- ============================================================

-- ---------- Identity ----------
CREATE TABLE IF NOT EXISTS tantric_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    google_id TEXT UNIQUE,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'seeker',
    is_active BOOLEAN DEFAULT 1,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_user_sub_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    sub_profile_id TEXT UNIQUE NOT NULL,
    relationship TEXT NOT NULL,
    profile_name TEXT NOT NULL,
    birth_year INTEGER, birth_month INTEGER, birth_day INTEGER,
    birth_hour REAL, birth_lat REAL, birth_lon REAL,
    birth_timezone TEXT,
    birth_date_confirmed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- Sessions & chat (AES-256-GCM + HMAC chain) ----------
CREATE TABLE IF NOT EXISTS tantric_chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    sub_profile_id TEXT,
    session_key_encrypted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content_encrypted TEXT,
    hmac_signature TEXT,
    previous_hash TEXT,
    yantra_svg TEXT,
    audio_file_path TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- Document vault ----------
CREATE TABLE IF NOT EXISTS tantric_profile_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    sub_profile_id TEXT,
    document_id TEXT UNIQUE NOT NULL,
    original_filename TEXT,
    stored_path TEXT,
    file_hash_sha256 TEXT,
    mime_type TEXT,
    file_size_bytes INTEGER,
    exif_stripped BOOLEAN DEFAULT 0,
    encryption_salt TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- Rate limiting ----------
CREATE TABLE IF NOT EXISTS tantric_rate_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    attempt_count INTEGER DEFAULT 0,
    window_start TIMESTAMP,
    blocked_until TIMESTAMP
);

-- ---------- Nashta Jataka (reverse birth-time search) ----------
CREATE TABLE IF NOT EXISTS tantric_nashta_jataka (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id TEXT,
    target_sub_profile_id TEXT,
    known_relative_sub_profile_id TEXT,
    relationship TEXT,
    search_window_years INTEGER,
    d12_constraint_signs TEXT,
    d9_cross_verification_signs TEXT,
    candidate_dates TEXT,
    selected_date TEXT,
    fitness_score REAL,
    uncertainty_years REAL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ---------- Consultation & engine outputs ----------
CREATE TABLE IF NOT EXISTS tantric_consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    sub_profile_id TEXT,
    question_summary TEXT,
    consultation_mode TEXT,
    response_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_natal_charts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id TEXT UNIQUE NOT NULL,
    sub_profile_id TEXT,
    birth_datetime TEXT,
    birth_lat REAL,
    birth_lon REAL,
    ayanamsha TEXT DEFAULT 'lahiri',
    chart_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_multi_engine_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id TEXT UNIQUE NOT NULL,
    chart_id TEXT,
    system_name TEXT,
    interpretation_text TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_past_life (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id TEXT UNIQUE NOT NULL,
    sub_profile_id TEXT,
    projection_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_yantra_prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id TEXT UNIQUE NOT NULL,
    sub_profile_id TEXT,
    yantra_type TEXT,
    svg_path TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_acoustic_prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id TEXT UNIQUE NOT NULL,
    sub_profile_id TEXT,
    f0_hz REAL,
    binaural_hz REAL,
    wav_path TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_safety_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id TEXT UNIQUE NOT NULL,
    query_text TEXT,
    verdict TEXT,
    matched_pattern TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_seeker_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id TEXT UNIQUE NOT NULL,
    consultation_id TEXT,
    rating INTEGER,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tantric_remedial_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet_name TEXT NOT NULL,
    mahavidya TEXT NOT NULL,
    avatar TEXT,
    bija_mantra TEXT,
    yantra_type TEXT,
    remedial_objective TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
