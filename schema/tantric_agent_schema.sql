-- Tantric AI Agent Schema
-- Oracle Cloud MySQL (myjob_agent database)
-- Applied: 2026-09-27
-- Server: 127.0.0.1:3307 (via SSH tunnel from Oracle VM)

-- ============================================
-- CONSULTATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_consultations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) UNIQUE NOT NULL,
    seeker_query TEXT NOT NULL,
    birth_year INT, birth_month INT, birth_day INT,
    birth_hour DOUBLE, birth_lat DOUBLE, birth_lon DOUBLE,
    birth_timezone VARCHAR(64), systems_used VARCHAR(255),
    confidence_score DOUBLE, interpretation_summary TEXT,
    yantra_prescribed VARCHAR(64), mantra_prescribed VARCHAR(255),
    audio_f0 DOUBLE, audio_binaural_diff DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- NATAL CHARTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_natal_charts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    sun_longitude DOUBLE, sun_rashi INT, sun_nakshatra INT, sun_pada INT,
    moon_longitude DOUBLE, moon_rashi INT, moon_nakshatra INT, moon_pada INT,
    mars_longitude DOUBLE, mars_rashi INT, mars_nakshatra INT, mars_pada INT,
    mercury_longitude DOUBLE, mercury_rashi INT, mercury_nakshatra INT, mercury_pada INT,
    jupiter_longitude DOUBLE, jupiter_rashi INT, jupiter_nakshatra INT, jupiter_pada INT,
    venus_longitude DOUBLE, venus_rashi INT, venus_nakshatra INT, venus_pada INT,
    saturn_longitude DOUBLE, saturn_rashi INT, saturn_nakshatra INT, saturn_pada INT,
    rahu_longitude DOUBLE, rahu_rashi INT, rahu_nakshatra INT, rahu_pada INT,
    ketu_longitude DOUBLE, ketu_rashi INT, ketu_nakshatra INT, ketu_pada INT,
    lagna_longitude DOUBLE, lagna_rashi INT, lagna_nakshatra INT, lagna_pada INT,
    atmakaraka_index INT, karakamsha_rashi INT, ishta_devata_id INT,
    compute_duration_ns BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES tantric_consultations(consultation_id)
) ENGINE=InnoDB;

-- ============================================
-- MULTI-ENGINE RESULTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_multi_engine_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    system_name VARCHAR(32) NOT NULL,
    house_lordship JSON, planetary_dignity JSON, effective_strength JSON,
    dasha_lord INT, bhukti_lord INT, confidence DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES tantric_consultations(consultation_id)
) ENGINE=InnoDB;

-- ============================================
-- PAST LIFE ANALYSIS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_past_life (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    d60_positions JSON,
    rahu_longitude DOUBLE, ketu_longitude DOUBLE,
    rahu_house INT, ketu_house INT,
    karmic_pattern TEXT, prarabdha_theme TEXT,
    confidence DOUBLE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES tantric_consultations(consultation_id)
) ENGINE=InnoDB;

-- ============================================
-- YANTRA PRESCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_yantra_prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    yantra_type VARCHAR(64) NOT NULL,
    svg_data LONGTEXT, svg_size INT, generation_time_us INT,
    deity_name VARCHAR(64), bija_mantra VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES tantric_consultations(consultation_id)
) ENGINE=InnoDB;

-- ============================================
-- ACOUSTIC PRESCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_acoustic_prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    fundamental_freq DOUBLE, binaural_diff DOUBLE,
    duration_seconds DOUBLE, brainwave_target VARCHAR(32),
    audio_file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES tantric_consultations(consultation_id)
) ENGINE=InnoDB;

-- ============================================
-- SAFETY AUDIT LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_safety_audit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64),
    query_text TEXT, safety_result VARCHAR(32),
    blocked_category VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- SEEKER FEEDBACK TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_seeker_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id VARCHAR(64) NOT NULL,
    rating INT, corrections TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES tantric_consultations(consultation_id)
) ENGINE=InnoDB;

-- ============================================
-- REMEDIAL MAPPING TABLE (Todala Tantra)
-- ============================================
CREATE TABLE IF NOT EXISTS tantric_remedial_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    planet_name VARCHAR(32) NOT NULL,
    mahavidya VARCHAR(64) NOT NULL,
    avatar VARCHAR(64), bija_mantra VARCHAR(32),
    yantra_type VARCHAR(64), remedial_objective TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- SEED DATA: Todala Tantra Remedial Mappings
-- ============================================
INSERT IGNORE INTO tantric_remedial_mapping (planet_name, mahavidya, avatar, bija_mantra, yantra_type, remedial_objective) VALUES
('Saturn', 'Kali', 'Krishna', 'Krim', 'kali_yantra', 'Relieves chronic delays, Sade-Sati afflictions'),
('Jupiter', 'Tara', 'Rama', 'Strim', 'tara_yantra', 'Resolves intellectual crises, Guru Chandal doshas'),
('Mercury', 'Tripura Sundari', 'Parashurama', 'Klim', 'sri_yantra', 'Resolves nervous imbalances, intellectual confusion'),
('Moon', 'Bhuvaneshvari', 'Vamana', 'Hrim', 'bhuvaneshvari_yantra', 'Calms emotional turbulence, psychological anxiety'),
('Mars', 'Bagalamukhi', 'Kurma', 'Hlim', 'bagalamukhi_yantra', 'Neutralizes active hostility, legal disputes'),
('Rahu', 'Chhinnamasta', 'Narasimha', 'Hum', 'chhinnamasta_yantra', 'Clears obsessive delusions, sudden shocks'),
('Ketu', 'Dhumavati', 'Varaha', 'Dhum', 'dhumavati_yantra', 'Alleviates poverty, isolation, deep depression'),
('Venus', 'Kamala', 'Buddha', 'Shrim', 'kamala_yantra', 'Corrects severe financial lack, marital discord'),
('Sun', 'Matangi', 'Rama', 'Aim', 'matangi_yantra', 'Promotes intellectual mastery, artistic refinement');

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_tantric_consultations_created ON tantric_consultations(created_at);
CREATE INDEX idx_tantric_consultations_id ON tantric_consultations(consultation_id);
CREATE INDEX idx_tantric_safety_audit_created ON tantric_safety_audit(created_at);
CREATE INDEX idx_tantric_remedial_planet ON tantric_remedial_mapping(planet_name);
