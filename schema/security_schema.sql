-- ============================================
-- TANTRIC AI AGENT - SECURITY SCHEMA
-- ============================================
-- MySQL 8.0+ / InnoDB (Oracle Cloud)
-- Server: 127.0.0.1:3307 (via SSH tunnel)
-- Database: myjob_agent
-- Applied: 2026-09-27

-- ============================================
-- USER AUTHENTICATION
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Argon2id hash
    role ENUM('seeker','practitioner','acharya','admin') DEFAULT 'seeker',
    is_active BOOLEAN DEFAULT TRUE,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB;

-- ============================================
-- USER SUB-PROFILES (Family Members)
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_user_sub_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    sub_profile_id VARCHAR(64) UNIQUE NOT NULL,
    relationship ENUM('self','father','mother','spouse','child','sibling','other') NOT NULL,
    profile_name VARCHAR(128) NOT NULL,
    birth_year INT, birth_month INT, birth_day INT,
    birth_hour DOUBLE, birth_lat DOUBLE, birth_lon DOUBLE,
    birth_timezone VARCHAR(64),
    birth_date_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tantric_users(user_id)
) ENGINE=InnoDB;

-- ============================================
-- DOCUMENT VAULT (Encrypted Files)
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_profile_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    sub_profile_id VARCHAR(64),
    document_id VARCHAR(64) UNIQUE NOT NULL,
    original_filename VARCHAR(255),
    stored_path VARCHAR(512) NOT NULL,
    file_hash_sha256 VARCHAR(64) NOT NULL,
    mime_type VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    exif_stripped BOOLEAN DEFAULT FALSE,
    encryption_salt VARCHAR(64),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tantric_users(user_id)
) ENGINE=InnoDB;

-- ============================================
-- CHAT SESSIONS (Encrypted)
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    sub_profile_id VARCHAR(64),
    session_key_encrypted VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tantric_users(user_id)
) ENGINE=InnoDB;

-- ============================================
-- CHAT MESSAGES (HMAC-Chained)
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(64) UNIQUE NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    role ENUM('user','assistant','system') NOT NULL,
    content_encrypted TEXT NOT NULL,
    hmac_signature VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),
    yantra_svg LONGTEXT,
    audio_file_path VARCHAR(512),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES tantric_chat_sessions(session_id)
) ENGINE=InnoDB;

-- ============================================
-- RATE LIMITING
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_rate_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    endpoint VARCHAR(64) NOT NULL,
    attempt_count INT DEFAULT 1,
    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blocked_until TIMESTAMP NULL,
    UNIQUE KEY uk_ip_endpoint (ip_address, endpoint)
) ENGINE=InnoDB;

-- ============================================
-- NASHTA JATAKA (Lost Horoscope)
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_nashta_jataka (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    target_sub_profile_id VARCHAR(64) NOT NULL,
    known_relative_sub_profile_id VARCHAR(64) NOT NULL,
    relationship VARCHAR(32) NOT NULL,
    search_window_years INT DEFAULT 29,
    d12_constraint_signs JSON,
    d9_cross_verification_signs JSON,
    candidate_dates JSON,
    selected_date JSON,
    fitness_score DOUBLE,
    uncertainty_years DOUBLE,
    status ENUM('pending','searching','resolved','failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL
) ENGINE=InnoDB;
