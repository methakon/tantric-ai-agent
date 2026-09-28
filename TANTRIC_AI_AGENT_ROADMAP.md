# Tantric AI Agent — Roadmap (AI Tantrik System Blueprint)

**Created:** 2026-09-27
**Source:** AI Tantrik System Blueprint.pdf
**Context:** Autonomous Cross-Tradition Tantrik and Divinatory AI Agent
**Persona:** Dharantrax Kapalik (ধরণ্ট্রাক্স কাপালিক) — erudite, contemplative, cross-tradition lineage guide

---

## Core Architecture

### Canonical Scriptural Foundations
- Vedic Matrix (Rigveda, Yajurveda, Atharvaveda)
- Shakta/Vaishnava Tantric Polarity (Kali Tantra, Radha Tantra)
- Subtle Body Energetics (72,000 Nadis, 3 primary channels, 7 chakras, 3 granthis)

### Cross-Cultural Esoteric Frameworks
- Vajrayana Buddhist Tantra (Guhyasamaja, Hevajra, Kalachakra)
- Chinese Tangmi/Zhenyan (Mahavairocana, Vajrasekhara)
- Taoist Neidan (Jing → Qi → Shen → Void → Dao)
- Islamic Esotericism (Ilm al-Ruhaniyat, Ilm al-Jafr, Ilm al-Huruf)

### Divinatory Systems
- Tantrik Jyotish (Todala Tantra — Mahavidya-planetary correspondences)
- Parashari Jyotish (BPHS, Vimshottari Dasha)
- Jaimini Jyotish (Chara Karakas, Atmakaraka, Karakamsha)
- Nadi Jyotish (Bhrigu Nadi, Chandra Kala Nadi)
- KP System (Krishnamurti Paddhati)
- Lal Kitab (Persian-Indian synthesis)
- Svara Vigyan (Shiva Svarodaya breath divination)
- Hasta Samudrika Shastra (palmistry)
- Anka Shastra (numerology)

---

## Implementation Phases

### Phase 1: Corpus Curation, Digital Archiving, and Text Normalization

**Goal:** Assemble authoritative multilingual corpus from academic archives.

**Sources:**
- Tantrik Texts (Arthur Avalon / Sir John Woodroffe)
- Kashmir Series of Texts and Studies (KSTS)
- Yoga-Tantra-Granthamala (Sampurnanand Sanskrit Vishwavidyalaya)
- BHU Faculty of Sanskrit Vidya Dharma Vijnan publications
- Muktabodha Indological Research Institute manuscripts
- National Mission for Manuscripts (Kriti Sampada portal)
- Digital Library of India
- IGNCA (Indira Gandhi National Centre for the Arts)

**Engineering Tasks:**
1. OCR for Devanagari, Bengali, Sarada scripts (Tesseract + deep learning)
2. Convert to Unicode + IAST transliteration
3. Extract verse-commentary pairs (Mula + Tika)
4. Standardize structural units for retrieval

**Hardware:** Current VM (7.6GB RAM, Xeon 20-core)
**Timeline:** 4-6 weeks
**Dependencies:** Tesseract OCR (Sanskrit-trained), Python Unicode tools

---

### Phase 2: Multimodal Engine — Sacred Geometry, Vision, Audio, and Sound Weaving

**Goal:** Build the complete multimodal engine covering vector geometry generation, computer vision identification, acoustic analysis, and generative sound synthesis.

---

#### 2A. Algorithmic Generation and Vector Drawing of Tantric Sacred Geometry

**Mathematical Foundations:**

**Sri Yantra (Most Complex):**
- 9 interlocking isosceles triangles (4 upward/Shiva, 5 downward/Shakti)
- Produces 43 secondary triangles, 8 concentric intersections
- 54 triple-intersection points (Marmas) — overdetermined non-linear system
- Must minimize coordinate distance ε→0 between converging line vectors
- Uses Gauss-Newton or Nelder-Mead numerical optimization
- Surrounded by: 8-petal lotus (Ashta-Dala Padma), 16-petal lotus (Shodasha-Dala Padma), 3 circles (Trivritta), Bhupura (4-gated citadel)

**Kali Yantra:**
- Central Bindu + 5 nested downward-pointing equilateral triangles
- 5 triangles = 5 Koshas (sheaths) + 5 Tattvas (elements)
- 8-petal lotus ring, 3 outer circles, 4-gated Bhupura

**Bagalamukhi & Shatkona Yantras:**
- Hexagram (Shatkona) = union of 2 equilateral triangles
- Triangle 1: {(x,y) | y = √3·x + c₁}
- Triangle 2: {(x,y) | y = -√3·x + c₂}
- Centered within yellow precinct with Bijaksharas

**Vector Graphics Pipeline:**
```
Input: Yantra type + parameters
  │
  ▼
[Coordinate Computation Engine]
  │─ Bhupura (stepped borders, 4 cardinal gates)
  │─ Concentric lotus circles (16-petal, 8-petal)
  │─ Interlocking polygon sets (triangles, hexagrams)
  │─ Central bindu + inscribed bijas
  │
  ▼
[Numerical Optimization]
  │─ Gauss-Newton / Nelder-Mead for 54 Marmas
  │─ Minimize ε for clean three-point intersections
  │─ Validate: no secondary error triangles
  │
  ▼
[SVG/Parametric Canvas Output]
  │─ Scalable vector graphics (SVG)
  │─ Embedded Devanagari/Siddham bijas
  │─ Color-coded element regions
  │
  ▼
[Delivery: UI rendering + construction details]
```

**Yantra Classes to Implement:**
1. Sri Yantra (9 triangles, 54 Marmas)
2. Kali Yantra (5 downward triangles)
3. Bagalamukhi Yantra (hexagram)
4. Shatkona Yantra (hexagram base)
5. Surya Yantra (solar geometry)
6. Tibetan Mandala (concentric squares + circles)
7. Islamic Wifq (3x3-9x9 magic squares)

---

#### 2B. Multimodal Computer Vision and Visual Identification Pipeline

**Dual-Stage Vision Stack:**
```
[Camera Stream] → [Preprocessing: Grayscale, Bilateral Filter, Canny Edge]
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
[Sacred Geometry Branch]          [Palmistry Branch (MediaPipe)]
- Contour Hierarchy Analysis      - 21 3D Joint Tracking
- Circular/Hough Transform        - Skin Mask & Crease Extraction
- ViT Classification Model        - Ridge Flow / Mount Elevation
        │                                   │
        └─────────────────┬─────────────────┘
                          ▼
   [Diagnostic Identification & Metadata Extraction]
```

**Yantra/Geometric Glyph Identification:**
1. Image preprocessing: Resize 640×640, bilateral filter, grayscale
2. Adaptive Otsu thresholding + Canny edge (T_low=50, T_high=150)
3. Topological hierarchy: findContours(RETR_TREE, CHAIN_APPROX_SIMPLE)
4. Concentricity check: centroids C_k = (x̄_k, ȳ_k), variance δ < 0.05·r_outer
5. Polygon categorization: outermost square = Bhupura, count circles via Hough
6. Deep learning: Fine-tuned ViT-B/16 or YOLO on sacred geometry classes
7. OCR: Devanagari, Tibetan dBu-can, Siddham, Nastaliq script extraction

**Hasta Samudrika Shastra (Computer Vision Palmistry):**
1. MediaPipe Hands: 21 3D landmarks in real time
2. Palm surface plane: wrist (0), index MCP (5), pinky MCP (17)
3. Mount detection:
   - Jupiter (Guru): below index finger (landmarks 5-6 base)
   - Saturn (Shani): below middle finger (landmarks 9-10 base)
   - Sun (Surya): below ring finger (landmarks 13-14 base)
   - Mercury (Budha): below pinky (landmarks 17-18 base)
   - Venus (Shukra): thenar eminence
   - Moon (Chandra): hypothenar eminence
4. Crease detection: Gabor filters (θ ∈ {0°, 45°, 90°, 135°}) + Hessian
5. Primary lines: Ayu Rekha (Life), Mastak Rekha (Head), Hridaya Rekha (Heart)
6. Classical signs (Lakshanas): Trishula, Matsya, Padma, Chakra

---

#### 2C. Microphone Audio Recognition and Mantric Acoustic Analysis

**Audio Processing Pipeline:**
```
[Audio Signal (44.1 kHz)] → [STFT / 128-band Mel-Spectrogram]
                                    │
       ┌────────────────────────────┴────────────────────────────┐
       ▼                                                         ▼
[Acoustic Engine (pYIN/CREPE)]                     [ASR Engine (Whisper)]
- Fundamental Frequency (F₀) Extraction            - Phoneme Alignment
- Vedic Accent Detection:                          - Bija Syllable Parsing
  Udatta, Anudatta, Svarita                       - Temporal Duration (Matra)
       │                                                         │
       └────────────────────────────┬────────────────────────────┘
                                    ▼
              [Pronunciation & Acoustic Validation Vector]
```

**Phonetic and Mantric Alignment:**
1. 128-band Mel-spectrograms: 2048-sample window, 512-sample hop
2. Whisper/Wav2Vec2 fine-tuned on Sanskrit phonology
3. Seed syllable segmentation (Aiṁ, Hrīṁ, Klīṁ, Chāmuṇḍāyai, Vicce)
4. Dirgha (long vowel) vs Hrasva (short vowel) measurement

**Vedic Tonal Registers (Svara Vigyan):**
- Udatta (Acute/High): positive F₀ deflection
- Anudatta (Grave/Low): negative F₀ deflection
- Svarita (Circumflex/Falling): rapid high→low transition

**Resonance Diagnostics (Anusvara/Nada):**
- Terminal nasal sound evaluation in OṀ, KRĪṀ
- Spectral energy ratio: 200-500 Hz band vs higher frequencies
- Proper Anusvara: concentrated resonance, low harmonic dispersion

---

#### 2D. Sound Weaving and Generative Acoustic Synthesis

**Synthesis Architecture:**
```
[Fundamental Pitch (f₀)]
        │
  ┌─────┴─────┐
  ▼           ▼
[Microtonal Just Intonation]    [Binaural Carrier Gen]
- 22-Shruti Interval Tuning     - Left Channel: f_c
- Tanpura Drone Overtones       - Right Channel: f_c + Δf
  │                             │
  └─────────────┬───────────────┘
                ▼
  [Vocal Formant Synthesis Engine]
  - Formant Filtering (F₁, F₂, F₃)
  - Nasal/Anusvara Shaping
                │
                ▼
  [Rendered Acoustic Output (.wav)]
```

**22-Shruti Just Intonation (Pure Harmonic Ratios):**
- Shadja (Sa): 1/1
- Shuddha Rishabha (Re): 9/8
- Shuddha Gandhara (Ga): 5/4
- Shuddha Madhyama (Ma): 4/3
- Panchama (Pa): 3/2
- Shuddha Dhaivata (Dha): 5/3
- Shuddha Nishada (Ni): 15/8

**Binaural Brainwave Entrainment:**
- Δf = |f_right - f_left|
- Alpha (8-12 Hz): calm alertness — Bhuvaneshvari, Lakshmi, Saraswati
- Theta (4-8 Hz): deep meditation — Kali, Chhinnamasta

**Formant Synthesis Engine:**
- Periodic saw/pulse waveforms → resonant formant filters
- Vocal transition: "A" → "U" → "M" → Silence
- 'A' formant: ~800 Hz
- 'U' formant: ~350 Hz
- 'M' formant: ~250 Hz (nasal resonance)

---

#### 2E. Scientific Research and Empirical Evidence

| Domain | Research | Method | Findings |
|--------|----------|--------|----------|
| Nonlinear Geometry | Kulaichev (1984), Moscow State | Topological/algebraic analysis | Exact Sri Yantra = overdetermined non-linear system; 54 clean Marmas = complex geometry |
| Cymatics | Hans Jenny (1967, 1972) | Tonoscope on fluid substrates | Vocalized AUM produces standing waves resembling concentric star-polygon geometries |
| Neuroimaging | Kalyani et al. (2011), NIMHANS | fMRI: OM vs meaningless controls | Bilateral limbic deactivation (amygdala, hippocampus); mimics vagus nerve stimulation |
| EEG | Mendiratta & Yadav (2024); Travis et al. | Multi-channel EEG during Trataka | Bilateral frontal theta (4-8 Hz), posterior alpha coherence (8-12 Hz); parietal-frontal synchronization |
| Respiratory | Weitzberg & Lundberg (2002), Karolinska | FeNO measurement during humming | Bhramari/Anusvara increased paranasal NO by 15×; vasodilator + antimicrobial effects |

---

#### 2F. Five-Stage Operational Framework

```
[Stage 1: Multimodal Sensor Diagnostic]
  ├── Video: Crop ROI, run ViT/OpenCV for Yantra or Palm
  └── Audio: Run Whisper/CREPE for Mantra phonetics & pitch
           │
           ▼
[Stage 2: Computational Synthesis & Horoscope Integration]
  ├── Ingest birth coordinates → pyswisseph (Lahiri)
  └── Query GraphRAG for planetary afflictions & deity affinities
           │
           ▼
[Stage 3: Parametric Vector Geometry Construction]
  ├── Calculate exact geometric coords with zero-gap optimization
  └── Embed Devanagari/Siddham bijas into vector chambers
           │
           ▼
[Stage 4: Acoustic Sound Weaving & Binaural Rendering]
  ├── Synthesize fundamental drone (f₀) via Just Intonation
  └── Layer binaural differences (Δf) & vocal formants
           │
           ▼
[Stage 5: Explanatory Dialogue & Safety Filtering]
  ├── Provide symbolic, historical, and mathematical context
  └── Verify compliance: Suppress curses and fatalistic claims
```

**Stage 1 — Multimodal Ingestion:**
- 1.1: Scan video for planar circular/square/polygonal contours
- 1.2: Crop, normalize, extract topological hierarchy, compare canonical models
- 1.3: If palm: MediaPipe Hands, 21 joints, crease lines, mount mapping
- 1.4: Process audio through STFT pipeline
- 1.5: Track F₀, classify accents (Udatta/Anudatta/Svarita)
- 1.6: Match phonemes to required Bijaksharas, report omissions

**Stage 2 — Astrological Synthesis:**
- 2.1: Pass birth data to pyswisseph (Lahiri Ayanamsha) for natal placements, Dasha, Atmakaraka
- 2.2: Traverse GraphRAG for challenged planets → Tantric remedial affinities (Todala Tantra)
- 2.3: Formulate remedial blueprint: yantra + bija + svara + contemplative focus

**Stage 3 — Geometric Generation:**
- 3.1: Compute vector coordinates; Sri Yantra: minimize 54 Marmas
- 3.2: Embed Devanagari/Siddham seed characters via SVG text elements
- 3.3: Output rendered vector + construction details

**Stage 4 — Sound Weaving:**
- 4.1: Set f₀ using Just Intonation (1/1, 3/2, 2/1)
- 4.2: Select Δf: 10 Hz (Alpha/stabilize) or 6 Hz (Theta/absorption)
- 4.3: Apply formant synthesis (A→U→M), shape Anusvara
- 4.4: Deliver stereo audio stream

**Stage 5 — Education & Safety:**
- 5.1: Frame with historical lineage, geometric symbolism, acoustic qualities
- 5.2: Cite scientific literature (Kulaichev, Jenny, NIMHANS, Karolinska)
- 5.3: Safety check: no harmful rituals, no fatalistic predictions, mental health protocol

---

**Hardware:** RTX 3060 12GB + 32GB RAM (for ViT classification, audio processing)
**Timeline:** 8-12 weeks
**Dependencies:** pyswisseph, OpenCV, MediaPipe, Whisper/CREPE, HuggingFace Transformers, Neo4j

---

### Phase 3: Alignment, Instruction Fine-Tuning, and Guardrail Integration

**Goal:** Train language model with Dharantrax Kapalik persona and safety protocols.

**Fine-tuning Corpus:**
- Classical commentaries (Abhinavagupta, Bhaskararaya)
- Academic curricula (BHU, SSVV)
- Dialogues framed as Dharantrax Kapalik persona
- Cross-cultural synthesis examples

**Safety Guardrails:**
1. **Prohibition of Harmful Rites:**
   - Reject: Marana (destruction), Vidveshana (enmity), Ucchatana (expulsion)
   - Reject: Coercive/non-consensual Vashikaran
   - Reframe toward: Shanti (pacification), Paushtika (nourishment)

2. **Non-Fatalistic Divinatory Guardrails:**
   - No death/mortality predictions
   - Medical disclaimers for health indicators
   - Deconstruct Kalsarpa/Mangal Dosha sensationalism

3. **Mental Health Protocol:**
   - Detect persecutory delusions, fragmented speech
   - De-escalate with somatic grounding exercises
   - Kundalini symptom mitigation (suspend Bhastrika, Kumbhaka)
   - Encourage professional healthcare consultation

**Hardware:** RTX 4060 Ti 16GB + 64GB RAM
**Timeline:** 8-12 weeks (after Phase 2)
**Dependencies:** LLM (Llama 3.1 8B or Qwen 2.5 7B), LoRA/QLoRA training

---

### Phase 4: Production Deployment and Continuous Evaluation

**Goal:** Deploy, monitor, and continuously improve the agent.

**Components:**
- Computational microservice (pyswisseph)
- GraphRAG pipeline
- Aligned model instances
- Automated validation against Rashtriya Panchang
- Safety guardrail monitoring
- Knowledge graph updates from new critical editions

**Hardware:** RTX 4060 Ti 16GB + 64GB RAM
**Timeline:** Ongoing (after Phase 3)

---

## Detailed Technical Components

### A. Subtle Body Energetics Model

**Three Primary Nadis:**
- Ida Nadi (left, lunar, parasympathetic)
- Pingala Nadi (right, solar, sympathetic)
- Sushumna Nadi (central, cerebrospinal)

**Seven Chakras:**
1. Muladhara (earth, 4 petals, survival)
2. Svadhisthana (water, 6 petals, subconscious)
3. Manipura (fire, 10 petals, willpower)
4. Anahata (air, 12 petals, identity)
5. Vishuddha (ether, 16 petals, discrimination)
6. Ajna (mental, 2 petals, perception)
7. Sahasrara (thousand petals, transcendence)

**Three Granthis:**
- Brahma Granthi (Muladhara — material attachment)
- Vishnu Granthi (Anahata — emotional attachment)
- Rudra Granthi (Ajna — intellectual individuation)

### B. Tantrik Jyotish — Mahavidya-Planetary Correspondences

| Mahavidya | Ruling Planet | Avatar | Remedial Objective | Bija Mantra |
|-----------|---------------|--------|-------------------|-------------|
| Kali | Saturn | Krishna | Chronic delays, Sade-Sati | Krīm |
| Tara | Jupiter | Rama | Intellectual crises, Guru Chandal | Strīm |
| Tripura Sundari | Mercury/Venus | Parashurama | Nervous imbalances | Klīm/Sauḥ |
| Bhuvaneshvari | Moon | Vamana | Emotional turbulence | Hrīm |
| Bhairavi | Ascendant/Mars | Balarama | Low vitality, self-doubt | Hsraiṁ |
| Chhinnamasta | Rahu | Narasimha | Obsessive delusions, addiction | Hūm |
| Dhumavati | Ketu/Saturn | Varaha | Poverty, isolation, depression | Dhūm |
| Bagalamukhi | Mars | Kurma | Hostility, legal disputes | Hlīm |
| Matangi | Sun | Rama | Intellectual mastery, paternal karma | Aiṁ |
| Kamala | Venus | Buddha | Financial lack, marital discord | Śrīm |

### C. Indian Divinatory Systems

1. **Parashari Jyotish:** BPHS, sidereal zodiac, 12 houses, Vimshottari Dasha
2. **Jaimini Jyotish:** Sign aspects, Chara Karakas, Atmakaraka, Karakamsha
3. **Nadi Jyotish:** Planetary conjunctions, Trines, karmic patterns
4. **KP System:** Placidus houses, nakshatra sub-lords
5. **Lal Kitab:** Fixed houses, blind planets, ancestral debts, Totkas

### D. Svara Vigyan — Breath Divination

- Ida (left/lunar): Peaceful, nourishing activities
- Pingala (right/solar): Physical exertion, technical tasks
- Sushumna (simultaneous): Spiritual transcendence, material failure

**Five Tattvas in Breath:**
- Prithvi (earth): Central flow, stabilizing, yellow
- Jala (water): Downward flow, cooling, white
- Tejas (fire): Upward flow, heating, red
- Vayu (air): Lateral flow, irregular, green/blue
- Akasha (ether): Dispersed, colorless, contemplation only

### E. Cross-Cultural Synthesis

| Tradition | Core Practice | Microcosmic Locus |
|-----------|---------------|-------------------|
| Hindu Shakta/Kaula | Mantra Japa, Kundalini ascent | Nadis, Chakras, Granthis |
| Hindu Vaishnava-Shakta | Devotional Rasa + Shakti axis | Heart center (Anahata) |
| Buddhist Vajrayana | Deity Yoga, Mudras | Central channel (Uma) |
| Chinese Tangmi | Three Mysteries (Sanmi) | Somatic-vocal-cognitive |
| Taoist Neidan | Microcosmic Orbit | Lower/Middle/Upper Dantians |
| Islamic Esotericism | Ilm al-Huruf, Wifq | Subtle Heart center (Qalb) |

---

## Current State Assessment

### What Exists in my-job-agent

1. **Jyotish Engine (partial):**
   - `src/astro/` — astronomy-engine based calculations
   - `astro-match.service.ts` — basic compatibility scoring
   - `panchanga.service.ts` — Panchanga/Tithi calculations
   - **Missing:** Sidereal zodiac (Lahiri Ayanamsha), Vimshottari Dasha, Jaimini Karakas, Nadi analysis

2. **AI Integration:**
   - `src/ai/` — AWS Bedrock provider
   - `ai-bedrock-provider.test.js` — Bedrock connectivity
   - **Missing:** GraphRAG, knowledge graph, Dharantrax Kapalik persona

3. **Trading Agent:**
   - `src/trading-agent/` — market data, pattern engine
   - **Missing:** Tantric market timing (Svara Vigyan integration)

4. **Job Application:**
   - `src/job-application/` — full application pipeline
   - **Missing:** Tantric career guidance (numerology, palmistry integration)

### What's Missing (Full Blueprint)

1. **Corpus:** No Sanskrit/Tantric texts ingested
2. **Knowledge Graph:** No ontology, no GraphRAG
3. **Computational Engine:** No pyswisseph, no sidereal calculations
4. **Divinatory Systems:** Only basic Parashari (partial)
5. **Safety Guardrails:** No harmful rite detection, no mental health protocol
6. **Persona:** No Dharantrax Kapalik training
7. **Cross-Cultural:** No Buddhist, Taoist, Islamic esoteric modules

---

## Hardware Requirements (Updated)

### Phase 1: Corpus Curation (Current VM OK)
- CPU: 20-core Xeon ✓
- RAM: 7.6GB (may need upgrade for large OCR batches)
- GPU: Not needed for text processing
- Storage: 1.8TB HDD ✓ (may need SSD for speed)

### Phase 2: Knowledge Graph + Engine (Step 3)
- GPU: RTX 3060 12GB (minimum)
- RAM: 32GB minimum
- Storage: 500GB NVMe SSD recommended

### Phase 3: LLM Fine-tuning (Step 3+)
- GPU: RTX 4060 Ti 16GB (recommended)
- RAM: 64GB recommended
- Storage: 1TB NVMe SSD

### Phase 4: Production (Step 3+)
- GPU: RTX 4060 Ti 16GB or cloud GPU
- RAM: 64GB
- Network: Low-latency API access

---

## Immediate Next Actions

### This Session
1. Install pyswisseph in .venv-ai (deterministic engine)
2. Install Neo4j Python driver (knowledge graph)
3. Begin corpus acquisition from digital repositories

### Week 1-2
1. Set up OCR pipeline for Sanskrit texts
2. Create initial ontology schema (Deity, Planet, Chakra, Mantra)
3. Build pyswisseph computational microservice prototype

### Week 3-4
1. Ingest Tantrik Texts (Arthur Avalon) into knowledge base
2. Map Mahavidya-planetary correspondences
3. Test sidereal chart calculation with sample birth data

### When Budget Allows (Step 3)
1. Purchase RTX 3060 12GB + 32GB RAM
2. Install CUDA drivers
3. Begin LLM fine-tuning with Dharantrax Kapalik persona

---

## Budget Summary

| Phase | Hardware Cost | Timeline |
|-------|---------------|----------|
| Phase 1 | ₹0 (current VM) | 4-6 weeks |
| Phase 2 | ₹37K-58K (GPU + RAM) | 6-8 weeks |
| Phase 3 | ₹65K-90K (better GPU + RAM) | 8-12 weeks |
| Phase 4 | Ongoing cloud costs | Ongoing |

**Total Hardware Investment:** ₹37K-90K depending on choices

---

*This roadmap follows the AI Tantrik System Blueprint — a comprehensive
cross-tradition Tantric and divinatory AI agent architecture.*
