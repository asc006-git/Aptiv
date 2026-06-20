<p align="center">
  <img src="https://img.shields.io/badge/APTIV-Talent_Intelligence_Platform-0d1117?style=for-the-badge&labelColor=161b22&color=58a6ff" alt="Aptiv" height="40"/>
</p>

<h1 align="center">
  A P T I V
</h1>

<p align="center">
  <strong>AI-Powered Talent Intelligence That Finds Who Keyword Filters Miss</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.42-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Pandas-2.3-150458?style=flat-square&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/NumPy-2.1-013243?style=flat-square&logo=numpy&logoColor=white" alt="NumPy"/>
  <img src="https://img.shields.io/badge/CPU_Only-Pass-2ea043?style=flat-square" alt="CPU Only"/>
  <img src="https://img.shields.io/badge/Public_Sandbox-Live-ff6f00?style=flat-square" alt="Sandbox"/>
  <img src="https://img.shields.io/badge/Validator-PASS-2ea043?style=flat-square" alt="Validator"/>
</p>

<p align="center">
  <a href="https://aptiv-ranker.streamlit.app"><strong>Live Sandbox</strong></a> &nbsp;&middot;&nbsp;
  <a href="https://github.com/asc006-git/Aptiv"><strong>Repository</strong></a> &nbsp;&middot;&nbsp;
  <img src="https://img.shields.io/badge/Submission-Ready-2ea043?style=flat-square" alt="Submission Ready"/>
</p>

---

## Executive Summary

**Aptiv** is an AI Talent Intelligence Platform that ranks, explains, and prioritizes **100,000 candidates** against any technical role — processing the entire pipeline in **~199 seconds on a single CPU core**, with zero GPU, zero LLM API calls, and zero network dependencies.

### The Problem

Traditional Applicant Tracking Systems (ATS) rely on **keyword matching** — they count resume hits against a job description and rank by overlap. This approach systematically fails in three ways:

| Failure Mode | What ATS Misses |
|:---|:---|
| **Keyword blindness** | Adjacent-skill candidates whose capabilities map directly to the role but use different terminology |
| **Hidden talent** | High-intent, high-availability candidates who are responsive and interview-ready but lack keyword density |
| **Visibility bias** | Underexposed experts with strong technical signals (GitHub, assessments) but low recruiter reach |

Modern hiring needs **intelligence**, not filtering. Recruiters need to know not just *who matches*, but *who to call first*, *why this person ranks here*, and *who the market is overlooking*.

### Aptiv vs. Traditional ATS

| Capability | Traditional ATS | Aptiv |
|:---|:---|:---|
| **Ranking method** | Keyword count / overlap score | 5-component weighted scoring across skill, experience, retrieval depth, behavior, and startup fit |
| **Hidden talent detection** | None | 6-component Hidden Gem engine with 5 candidate categories |
| **Recruiter prioritization** | None — all ranked equally | RAP engine with urgency scoring and action instructions |
| **Explainability** | "Keyword score: 0.83" | Full narrative with score breakdown, strengths, concerns, JD alignment, and next-step recommendation |
| **Honeypot detection** | None | Heuristic detection of inflated timelines, skill claims, and title mismatches |
| **Narrative output** | None | 10 archetypes, 8 templates, hash-varied phrasing — every briefing is unique |
| **Throughput** | Varies | 100K candidates in ~199s on a single CPU core |
| **Dependencies** | Cloud APIs, LLMs, GPU | 3 Python packages, CPU only, fully offline |

### Why Aptiv Is Different

Aptiv models candidate quality across **five independent dimensions** — then layers **risk detection**, **Hidden Gem identification**, and **recruiter action prioritization** on top. Every ranking decision comes with a **recruiter-readable narrative** explaining the score, the strengths, the concerns, and the recommended next step.

### Business Value

- **Surface hidden talent** that keyword filters systematically miss
- **Prioritize recruiter effort** — know exactly who to contact first and why
- **Explainable decisions** — every score is auditable and recruiter-interpretable
- **100K candidates in 200 seconds** — production-grade throughput on consumer hardware

---

## Problem Statement

### Why Keyword Matching Fails

Resume keyword matching treats hiring as a **counting problem**: more keyword overlap = better candidate. This creates four critical blind spots:

**1. The Resume Keyword Limitation**
A search-infrastructure engineer who built dense retrieval pipelines at scale but never used "Pinecone" by name gets ranked below a candidate who listed the buzzword but never shipped a system. ATS rewards vocabulary, not capability.

**2. The Hidden Candidate Problem**
Candidates who are highly responsive, complete interviews reliably, and can start immediately — but whose resumes lack perfect keyword density — are buried below keyword-optimized profiles that may never respond to outreach.

**3. The Recruiter Prioritization Problem**
Even after ranking, a recruiter staring at 100 shortlisted candidates has no signal for *who to contact first*. A top-ranked candidate with a 120-day notice period and 20% response rate is functionally less valuable this quarter than a #50 candidate who's open-to-work, responds within hours, and can start in 15 days.

**4. The Explainability Problem**
When a recruiter asks *"Why is this person ranked #7?"* — traditional ATS systems have no answer beyond "keyword score: 0.83." Without transparency, recruiters can't trust the ranking, can't override it intelligently, and can't explain their shortlist to hiring managers.

### What Modern Hiring Needs

Not better **filtering** — better **intelligence**. A system that understands capability depth, behavioral signals, market positioning, and recruiter workflow — then communicates all of it in plain language.

---

## How Aptiv Works

The Aptiv pipeline processes candidates through **nine sequential stages**, from raw data to recruiter-ready output:

```
+-------------------------------------+
|  1. Upload Dataset                  |  JSON / JSONL candidate profiles
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  2. Candidate Parsing               |  ~60 structured features extracted
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  3. Feature Extraction              |  Skills, disqualifiers, behavioral
|                                     |  signals, data quality flags
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  4. Weighted Scoring                |  5-component composite score [0, 1]
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  5. Hidden Gem Detection            |  6-component undervalued candidate
|                                     |  identification (5 categories)
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  6. RAP Prioritization              |  4-component recruiter urgency
|                                     |  scoring (5 priority levels)
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  7. Narrative Intelligence          |  10 archetypes x 8 templates x
|                                     |  hash-varied phrasing. Zero LLMs.
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  8. Leaderboard                     |  Top 100 ranked with tier,
|                                     |  archetype, and explainability
+------------------+------------------+
                   |
                   v
+-------------------------------------+
|  9. CSV Export                      |  Validator-compliant submission
|                                     |  (candidate_id, rank, score,
|                                     |  reasoning)
+-------------------------------------+
```

---

## Technology Stack

| Layer | Technology | Why This Choice |
|:---|:---|:---|
| **Frontend** | Streamlit 1.42 | Rapid interactive dashboards with zero frontend boilerplate. Native dark theme, file upload, and export support. |
| **Backend** | Python 3.10+ | Industry-standard ML/data processing language with rich ecosystem for numerical computation. |
| **Data Processing** | Pandas 2.3, NumPy 2.1 | Vectorized operations across 100K candidates — no row-level loops in scoring. DataFrame-native pipeline architecture. |
| **Deployment** | Streamlit Cloud | Zero-config deployment with public URL. No Docker, no server provisioning, no infrastructure management. |
| **Version Control** | Git + GitHub | Standard collaborative development with full commit history and public repository access. |

### Design Constraints (By Choice)

| Constraint | Rationale |
|:---|:---|
| **No GPU** | Scoring, detection, and narrative generation are all deterministic rule-based systems — GPU acceleration provides no benefit. |
| **No LLM API calls** | Narratives are generated via hash-varied template composition. Every output is deterministic, reproducible, and auditable — no stochastic variance. |
| **No network at runtime** | The entire pipeline runs offline after data load. No external API calls during ranking. |
| **Three dependencies** | `streamlit`, `pandas`, `numpy` — minimal attack surface, fast install, reproducible environments. |

---

## Core Features

### 1. Multi-Factor Ranking Engine

| | |
|:---|:---|
| **Purpose** | Rank candidates by genuine capability across multiple independent dimensions, not keyword count |
| **Inputs** | ~60 parsed features per candidate: skills, experience, behavioral signals, data quality flags |
| **Outputs** | Composite score [0, 1] with full sub-score breakdown |
| **Business Value** | Surfaces candidates whose real capability exceeds their keyword density — the people keyword filters miss |

---

### 2. Hidden Gem Detection

| | |
|:---|:---|
| **Purpose** | Identify undervalued candidates whose true potential is masked by conventional ranking |
| **Inputs** | Behavioral excellence, skill adjacency, technical evidence, growth trajectory, market demand, recruitability |
| **Outputs** | Hidden Gem Score (0-100), category label, recruiter briefing narrative |
| **Business Value** | Unlocks a talent pool invisible to keyword-based systems — sourcing advantage over competitors using traditional ATS |

---

### 3. Recruiter Action Prioritization (RAP)

| | |
|:---|:---|
| **Purpose** | Answer: *"Of 100,000 candidates, who should I contact first?"* |
| **Inputs** | Engagement velocity, availability, conversion likelihood, match baseline |
| **Outputs** | RAP Score (0-100), priority tier, action instruction, one-sentence rationale |
| **Business Value** | Converts ranking into actionable recruiter workflow — reduces time-to-first-contact for highest-ROI candidates |

---

### 4. Explainability Engine

| | |
|:---|:---|
| **Purpose** | Make every ranking decision transparent, auditable, and recruiter-interpretable |
| **Inputs** | Sub-scores, pool statistics, candidate signals, JD alignment markers |
| **Outputs** | Score breakdown, pool-relative percentile, strength/concern decomposition, JD alignment text |
| **Business Value** | Builds recruiter trust in AI-assisted decisions — explainable rankings that hiring managers can defend |

---

### 5. Narrative Intelligence

| | |
|:---|:---|
| **Purpose** | Generate unique, recruiter-facing candidate briefings without any LLM |
| **Inputs** | Archetype classification (10 types), rank tier (5 levels), candidate-specific signals |
| **Outputs** | Full narrative with JD alignment, score breakdown, strengths, concerns, recruiter action, and next-step recommendation |
| **Business Value** | Recruiter reads one paragraph per candidate instead of scanning raw data — 10x faster shortlist review |

---

### 6. Sandbox Platform

| | |
|:---|:---|
| **Purpose** | Interactive web interface for exploring the full pipeline output |
| **Inputs** | JSON/JSONL candidate file upload (or built-in 50-candidate demo) |
| **Outputs** | Leaderboard, Hidden Gems, RAP queue, candidate detail panels, CSV exports |
| **Business Value** | Judges and stakeholders can verify the system end-to-end in a browser — no local setup required |

---

### 7. CSV Export Engine

| | |
|:---|:---|
| **Purpose** | Generate submission-compliant output for programmatic evaluation |
| **Inputs** | Ranked DataFrame with narratives |
| **Outputs** | CSV with `candidate_id, rank, score, reasoning` for top 100 candidates |
| **Business Value** | Deterministic, reproducible, validator-compliant output — same input always produces same output |

---

## System Architecture

Each module in the pipeline has a single responsibility and a clean input/output contract:

| Module | Responsibility | Input | Output | Importance |
|:---|:---|:---|:---|:---|
| **`candidate_parser.py`** | Streaming JSONL parser and feature extractor | Raw candidate JSON/JSONL | Flat DataFrame with ~60 features per candidate | Foundation — all downstream modules depend on the quality and completeness of parsed features |
| **`scorer.py`** | Multi-factor weighted composite scoring | Parsed DataFrame | DataFrame with 5 sub-scores, risk penalty, and final score [0, 1] | Core ranking logic — determines candidate order |
| **`hidden_gem_detector.py`** | Undervalued candidate identification | Scored DataFrame | DataFrame with HG score (0-100), category, and narrative | Unique value proposition — surfaces talent invisible to keyword systems |
| **`rap_engine.py`** | Recruiter urgency and outreach prioritization | Scored + HG DataFrame | DataFrame with RAP score (0-100), priority tier, action, rationale | Converts ranking into actionable recruiter workflow |
| **`narrative_generator.py`** | Deterministic candidate briefing generation | Full enriched DataFrame | DataFrame with archetype, tier, narrative, signals, concerns, JD text | Explainability layer — makes AI decisions human-readable |
| **`generate_submission.py`** | CLI pipeline orchestrator | Input file path + output path | Submission CSV + console summary | Orchestrates the full pipeline in a single command |
| **`app.py`** | Streamlit interactive sandbox | User file upload or demo data | Interactive web dashboard with exports | Stakeholder-facing verification and exploration interface |

### Pipeline Flow

```
candidate_parser.py --> scorer.py --> hidden_gem_detector.py --> rap_engine.py --> narrative_generator.py
                                                                                          |
                                                                          +---------------+---------------+
                                                                          |                               |
                                                                          v                               v
                                                                  generate_submission.py              app.py
                                                                  (CLI -> CSV export)            (Sandbox UI)
```

---

## Scoring Engine

### Component Weights

| Component | Weight | What It Measures | Key Signals |
|:---|:---:|:---|:---|
| **Skill Match** | `0.40` | JD keyword alignment | 70% mandatory (vector DBs, embeddings, evaluation, Python) + 30% preferred (LLM fine-tuning, learning-to-rank, distributed systems, NLP/IR) |
| **Production Experience** | `0.25` | Shipped-system track record | Years of experience capped at 8; penalized for pure research (0.1x) or consulting-only (0.7x) |
| **Retrieval / Ranking** | `0.15` | Domain-specific depth | Binary: vector DB (0.4) + embeddings/dense retrieval (0.4) + NLP/IR (0.2) |
| **Behavioral Score** | `0.10` | Engagement and responsiveness | Recruiter response rate (40%) + login recency (30%) + interview completion (20%) + open-to-work (10%) |
| **Startup Fit** | `0.10` | Founding-team compatibility | Base 1.0; penalized for title-chaser (-0.5) or consulting-only (-0.4) |

### Risk Penalties

| Flag | Penalty | Source |
|:---|:---:|:---|
| Chronology error | **-0.30** | Employment timeline inconsistency |
| Salary error | **-0.30** | Salary expectation out of range |
| Trust error | **-0.20** | Known profile data quality issue |
| Honeypot: timeline inflated | **-0.30** | Suspiciously rapid career progression |
| Honeypot: skill inflated | **-0.30** | Unrealistic skill breadth claims |
| Honeypot: title mismatch | **-0.30** | Title does not match experience level |

### Final Score Formula

```
Final Score = 0.40 x SkillMatch
            + 0.25 x ProductionExp
            + 0.15 x RetrievalRanking
            + 0.10 x Behavioral
            + 0.10 x StartupFit
            - RiskPenalty

Clipped to [0.0, 1.0]
```

### Honeypot Detection

The dataset contains synthetic trap candidates with intentionally inflated timelines, unrealistic skill breadth, or title-to-experience mismatches. These are detected via heuristic rules during parsing and penalized in scoring. The `flag_duplicate_identity` signal (informational only) detects a synthetic dataset artifact — repeated name generation from a limited 50-name pool — and is **explicitly excluded from scoring penalties**.

---

## Hidden Gem Engine

### What Are Hidden Gems?

Hidden Gems are candidates whose **true potential is not reflected in their keyword-based rank**. They score well on behavioral, technical, or market signals that traditional keyword systems ignore — making them high-value sourcing targets that competitors overlook.

### Why They Matter

In a 100,000-candidate pool, keyword ranking reliably surfaces the top ~2% who have perfect resume-JD overlap. But the next tier — candidates with genuine capability masked by different terminology, lower platform visibility, or non-traditional career paths — gets systematically buried. Hidden Gem detection recovers this lost talent.

### Detection Methodology

The engine computes a **0-100 composite score** across 6 weighted components:

| Component | Weight | What It Captures |
|:---|:---:|:---|
| Behavioral Excellence | **30%** | High engagement, responsiveness, and reliability signals |
| Skill Adjacency | **20%** | Peaks near 0.4 skill match — not perfect overlap, but meaningful proximity |
| Technical Evidence | **20%** | GitHub activity + skill assessment scores as independent validation |
| Growth Trajectory | **15%** | Startup fit as proxy for learning velocity and ownership mentality |
| Market Demand | **10%** | Profile views + recruiter saves (log-scaled) |
| Recruitability | **5%** | Open-to-work flag + willingness to relocate |

Candidates scoring **>= 60** are classified into **5 mutually exclusive categories**:

### Hidden Gem Categories

| Category | Detection Criteria | Recruiter Value |
|:---|:---|:---|
| **Emerging Specialist** | Strong skill assessments but <= 4 JD keyword matches | Technical competence beyond resume keywords — depth over breadth |
| **Growth Candidate** | 2-5 YoE, behavioral score >= 0.75, startup fit >= 0.7 | High ceiling, coachable, motivated — ramps quickly in fast environments |
| **High Intent Candidate** | Open to work, response rate >= 80%, interview rate >= 80%, active within 30 days | Ready to move, low friction to engage — ideal for urgent hires |
| **Underexposed Expert** | Skill match >= 0.5, low visibility (< 10 views + saves), GitHub >= 50 | Strong technical signals overlooked by the market — sourcing edge |
| **Startup Builder** | Startup fit >= 0.8, distributed systems match, GitHub >= 50, willing to relocate | Full-stack ownership mentality — fits high-autonomy, ambiguous environments |

Each category includes a tailored **2-3 sentence recruiter briefing** explaining why the candidate is valuable despite their ranking position.

---

## RAP Engine

### Why Recruiter Prioritization Matters

Ranking tells you **who's best**. Prioritization tells you **who to call first**. A top-ranked candidate with a 120-day notice period and 20% response rate may be functionally unreachable this quarter — while a #50 candidate who's open-to-work, responds within hours, and has a 15-day notice period is a hire waiting to happen.

RAP converts ranking into **recruiter workflow**.

### RAP Methodology

The RAP Score (0-100) is computed from **4 components**:

| Component | Max Points | Key Signals |
|:---|:---:|:---|
| **Engagement Velocity** | 35 | Response rate (40%), response speed in hours (25%), interview rate (20%), login recency (15%) |
| **Availability** | 25 | Open to work (40%), notice period (35%), relocation willingness (15%), work mode flexibility (10%) |
| **Conversion Likelihood** | 20 | Offer acceptance rate (35%), interview rate (25%), GitHub activity (20%), profile completeness (20%) |
| **Match Baseline** | 20 | Final ranking score (capped) |

### RAP Priority Categories

| RAP Score | Priority | Implied Recruiter Action |
|:---|:---|:---|
| **>= 80** | Contact Immediately | Reach out within 24 hours |
| **65 - 79** | Priority Outreach | Schedule screen this week |
| **45 - 64** | Standard Outreach | Add to active pipeline |
| **25 - 44** | Long-Term Nurture | Monitor for re-engagement |
| **< 25** | Do Not Prioritize | Deprioritize in favor of higher-ROI candidates |

Each RAP assignment includes a **specific action instruction** (e.g., *"Message NOW. Candidate is highly responsive and available. Signals: 85% response rate, open to work, 15-day notice."*) and a **one-sentence rationale**.

---

## Explainability Engine

### Why Transparency Matters

AI-assisted hiring tools that produce opaque scores fail the stakeholder trust test. Recruiters won't act on a number they can't explain. Hiring managers won't approve candidates sourced by a black box. Compliance teams won't sign off on systems they can't audit.

Aptiv makes every ranking decision **fully transparent**:

### Explainability Components

| Component | What It Provides |
|:---|:---|
| **Score Breakdown** | Sub-component scores (skill match, production experience, retrieval/ranking, behavioral, startup fit) visible per candidate — weighted contribution to final score |
| **Strength Analysis** | Up to 5 positive signals extracted from candidate data — hash-varied phrasing from 12+ signal banks ensures no two candidates read identically |
| **Concern Detection** | Risk flags, disqualifiers, and subtle signals (low response rate, incomplete profile, missing GitHub) surfaced with context |
| **Recruiter Guidance** | Archetype classification (10 types), tier assignment (5 levels), action recommendation, and next-step instruction |
| **Narrative Intelligence** | Full recruiter-facing briefing using 8 structurally distinct templates x hash-varied phrasing. Includes JD alignment markers, pool-relative percentile, and at least one genuine concern per candidate |

### Pool-Relative Percentile

Every candidate's score is contextualized against the **full 100K pool** — not just the top 100. A candidate ranked #15 with a skill match 0.18 above the pool mean and a behavioral score 0.12 below the pool mean gets that differential called out explicitly.

### JD Alignment

Specific JD phrases — founding-team fit, production-over-research preference, startup DNA — are matched against candidate signals and surfaced as alignment markers in the narrative.

---

## Sandbox Platform

### Live URL

> **[https://aptiv-ranker.streamlit.app](https://aptiv-ranker.streamlit.app)**

### Platform Features

| View | What It Shows |
|:---|:---|
| **Dataset Upload** | Drop a JSON/JSONL candidate file, or use the built-in 50-candidate demo dataset |
| **Ranking Pipeline** | Run the full parse > score > rank > HG > RAP > narratives pipeline with real-time progress |
| **Leaderboard** | Top 100 ranked candidates with score, archetype, tier, and expandable detail panels |
| **Hidden Gems** | Filtered view of all Hidden Gem candidates with category labels and recruiter briefings |
| **RAP Queue** | Sorted by RAP score with priority labels, action instructions, and rationales |
| **Explainability** | Per-candidate: sub-score breakdown, positive signals, concerns, full narrative |
| **Candidate Comparison** | Side-by-side comparison of shortlisted candidates |
| **Export Center** | Download Ranked CSV, Hidden Gems CSV, RAP Priorities CSV, and Recruiter Shortlist CSV |

Configuration: headless mode, CORS disabled, dark theme. Falls back to `data/sample_candidates.json` (50 candidates) when the full 465 MB dataset is unavailable.

### Judge Verification Flow

For hackathon judges and evaluators, here is the recommended verification path:

```
1. Visit  ->  https://aptiv-ranker.streamlit.app
2. The demo dataset (50 candidates) loads automatically
3. Click "Run Pipeline" to execute the full ranking flow
4. Review the Leaderboard — expand any candidate to see full narrative
5. Switch to Hidden Gems — verify detection categories and briefings
6. Switch to RAP Queue — verify prioritization logic and actions
7. Open any candidate detail — verify score breakdown and explainability
8. Export CSVs — verify column structure and data integrity
9. (Optional) Upload a custom JSON/JSONL file to test with different data
```

No local setup, no API keys, no login required.

---

## Screenshots

### Dataset Upload

Upload candidate data via drag-and-drop. Supports JSON, JSONL, and CSV formats. Includes pool overview with experience distribution, location breakdown, and schema validation.

<p align="center">
  <img src="assets/screenshots/01_dataset_upload.png" alt="Aptiv — Dataset Upload and Ingestion Portal" width="100%"/>
</p>

---

### Leaderboard

Top candidates ranked by composite score. Each card shows rank, final score, archetype tags (Elite Match, Recruiter Favorite, Production Veteran), and quick-action buttons for analysis and shortlisting.

<p align="center">
  <img src="assets/screenshots/02_leaderboard.png" alt="Aptiv — Talent Leaderboard with Candidate Cards" width="100%"/>
</p>

---

### Candidate Analysis

Deep-dive intelligence panel for any candidate. Includes identity, experience, RAP analysis, skill tags, strengths, risks, full score breakdown with weighted sub-scores, and recruiter recommendation narrative.

<p align="center">
  <img src="assets/screenshots/03_candidate_analysis.png" alt="Aptiv — Candidate Intelligence Panel with Score Breakdown" width="100%"/>
</p>

---

### Exports and Validation

Export center with one-click CSV downloads (Submission, Recruiter Shortlist, Hidden Gems, RAP Priorities). Includes built-in validation panel showing compliance status for pool size, monotonicity, tie-breaking, and reasoning quality.

<p align="center">
  <img src="assets/screenshots/04_exports_validation.png" alt="Aptiv — Export Center and Submission Validation" width="100%"/>
</p>

---

## Performance Benchmarks

Tested on **4-core CPU, 16 GB RAM, Windows 10** — no GPU, no network, no external services.

### Overall Performance

| Metric | Result |
|:---|:---|
| Total pipeline runtime (100K candidates) | **~199 seconds** |
| Peak DataFrame memory | **~205 MB** |
| Candidates processed | **100,000** |
| Features extracted per candidate | **~60** |
| Output rows (submission CSV) | **100** |
| Execution model | **Deterministic, CPU-only** |
| Network dependency | **None** |

### Stage-Level Breakdown

| Stage | Time | % of Total | Description |
|:---|:---:|:---:|:---|
| Parsing | ~130s | 65% | Streaming JSONL to ~60 features per candidate |
| Scoring | ~0.2s | <1% | Vectorized 5-component scoring |
| Hidden Gem Detection | ~14s | 7% | 6-component scoring + category classification |
| RAP Computation | ~30s | 15% | 4-component urgency scoring + action generation |
| Narrative Generation | ~23s | 12% | Template selection + hash-varied narrative composition |
| Export + Overhead | ~2s | 1% | CSV serialization + cleanup |

### Resource Constraints

| Constraint | Status |
|:---|:---|
| GPU Required | No |
| Network Required | No |
| LLM API Required | No |
| External Services | None |
| Max Memory | **~205 MB** |
| Target Hardware | Consumer-grade laptop |

---

## Submission Compliance

| Requirement | Status | Detail |
|:---|:---:|:---|
| Validator compliance | **PASS** | All checks pass with zero warnings |
| Top 100 candidates | **PASS** | Exactly 100 rows exported |
| Score range [0, 1] | **PASS** | Range: 0.8435 - 0.9865 |
| Monotonically non-increasing scores | **PASS** | Verified — no rank inversions |
| Tie-breaking by `candidate_id` ASC | **PASS** | Verified — deterministic ordering |
| All `candidate_id` values unique | **PASS** | 100/100 unique |
| All `candidate_id` values exist in source | **PASS** | All mapped to source data |
| All reasoning non-empty | **PASS** | 100/100 populated |
| All reasoning unique | **PASS** | 100/100 unique narratives |
| Deterministic ranking | **PASS** | Same input produces same output |
| Reproducible pipeline | **PASS** | Single command, no external dependencies |
| Honeypot detection rate | **PASS** | Synthetic traps identified and penalized |

### Compliance Summary

```
+----------------------+--------+
|  Validator Status     |  PASS  |
|  Sandbox              |  PASS  |
|  Metadata             |  PASS  |
|  CSV Format           |  PASS  |
|  Reasoning Quality    |  PASS  |
|  Honeypot Rate        |  PASS  |
+----------------------+--------+
```

---

## Repository Structure

```
Aptiv/
|-- app.py                          # Streamlit sandbox (interactive platform)
|-- generate_submission.py          # CLI pipeline orchestrator
|-- candidate_parser.py             # Feature extraction engine (~60 features)
|-- scorer.py                       # Multi-factor weighted scoring
|-- hidden_gem_detector.py          # Hidden Gem detection (6-component score)
|-- rap_engine.py                   # Recruiter Action Prioritization
|-- narrative_generator.py          # Narrative intelligence (10 archetypes, 8 templates)
|-- benchmark_parser.py             # Parser performance benchmarking
|-- EDA.ipynb                       # Exploratory data analysis notebook
|-- requirements.txt                # Dependencies: streamlit, pandas, numpy
|-- submission_metadata.yaml        # Challenge metadata
|-- Adhyatma_Singh_Chauhan.csv      # Generated submission (100K dataset)
|-- README.md                       # This document
|-- .gitignore
|-- .streamlit/
|   +-- config.toml                 # Streamlit deployment configuration (dark theme)
|-- assets/
|   +-- screenshots/                # Platform screenshots for documentation
+-- data/
    |-- sample_candidates.json      # 50-candidate demo dataset
    |-- candidates.jsonl            # 100,000 candidates (465 MB, gitignored)
    |-- candidate_schema.json       # JSON schema reference
    |-- validate_submission.py      # Official submission validator
    |-- sample_submission.csv       # Reference submission format
    |-- job_description.docx        # Challenge job specification
    |-- redrob_signals_doc.docx     # Redrob behavioral signals documentation
    |-- submission_spec.docx        # Submission specification document
    |-- submission_metadata_template.yaml  # Metadata template
    +-- README.docx                 # Data directory documentation
```

---

## Installation

### Prerequisites

- Python 3.10+
- No GPU required
- No API keys required

### Setup

```bash
# Clone the repository
git clone https://github.com/asc006-git/Aptiv.git
cd Aptiv

# Install dependencies (3 packages only)
pip install -r requirements.txt
```

### Run the Sandbox

```bash
streamlit run app.py
```

Opens the interactive ranking platform in your browser. Uses the 50-candidate sample by default; upload a custom JSON/JSONL file for full analysis.

### Generate Submission

```bash
# Full dataset (100,000 candidates)
python generate_submission.py --input data/candidates.jsonl --output Adhyatma_Singh_Chauhan.csv

# Quick demo (50 candidates)
python generate_submission.py
```

### CLI Options

| Argument | Default | Description |
|:---|:---|:---|
| `--input` | `data/sample_candidates.json` | Input file (.json or .jsonl) |
| `--output` | `submission.csv` | Output CSV path |
| `--temp-jsonl` | `data/temp_candidates.jsonl` | Temp file for JSON to JSONL conversion |
| `--top-k` | `20` | Number of top candidates to display in console |

### Validate Submission

```bash
python data/validate_submission.py Adhyatma_Singh_Chauhan.csv
```

Expected output: **`Submission is valid.`**

---

## Deployment

### Streamlit Cloud

Aptiv is deployed on **Streamlit Cloud** at:

> **[https://aptiv-ranker.streamlit.app](https://aptiv-ranker.streamlit.app)**

### Deployment Steps

1. Push code to GitHub repository
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set `app.py` as the main file
4. Deploy — Streamlit Cloud auto-installs from `requirements.txt`

### Sandbox Requirements

| Requirement | Status |
|:---|:---|
| Public URL | `https://aptiv-ranker.streamlit.app` |
| No login required | Public access |
| Demo data included | 50-candidate sample bundled |
| Dark theme | Configured via `.streamlit/config.toml` |
| Headless mode | Server-side rendering |

---

## Future Roadmap

| Phase | Enhancement | Description |
|:---|:---|:---|
| **v2.0** | ATS Integrations | Webhook-based ingestion from Greenhouse, Lever, and Ashby for live candidate scoring |
| **v2.1** | Talent Graph Analytics | Cross-candidate relationship modeling — shared employers, schools, skill clusters — for team-building insights |
| **v2.2** | Interview Prediction | ML-based interview stage outcome prediction using RAP signals as features |
| **v3.0** | LLM-Assisted Workflows | Optional LLM enhancement for narrative refinement while keeping ranking deterministic |
| **v3.1** | Multi-Role Profiles | YAML/JSON-based weight configuration for different role families (ML Engineer, PM, Designer) |
| **v4.0** | Streaming Architecture | Incremental scoring for datasets exceeding 1M candidates without full reprocessing |

---

## Why Aptiv Matters

### The Hiring Intelligence Gap

The recruiting industry processes millions of candidates daily through systems that understand vocabulary but not capability, that count keywords but can't explain decisions, and that rank by overlap but can't tell a recruiter who to call first.

Aptiv closes that gap.

| Impact Area | What Aptiv Delivers |
|:---|:---|
| **Hidden Talent Discovery** | 5-category detection system that surfaces candidates invisible to keyword filters — the talent your competitors are systematically missing |
| **Recruiter Efficiency** | RAP converts a ranked list into an actionable workflow — priority, action, rationale — so recruiters spend time on the candidates most likely to convert |
| **Explainable Ranking** | Every score is decomposed, every narrative is unique, every decision is auditable — from board-level compliance to individual recruiter trust |
| **Hiring Intelligence** | Not a filter. Not a keyword counter. An intelligence layer that understands capability depth, behavioral signals, market positioning, and recruiter workflow |

<p align="center">
  <strong>Aptiv doesn't just rank candidates. It tells you who to hire, who you're overlooking, and why.</strong>
</p>

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial applications, subject to the terms of the MIT License.

---

<p align="center">
  <sub>Built by <strong>Adhyatma Singh Chauhan</strong> &middot; Solo Developer &middot; ML Engineer</sub><br/>
  <sub>
    <a href="https://github.com/asc006-git/Aptiv">GitHub</a> &middot; 
    <a href="https://aptiv-ranker.streamlit.app">Live Sandbox</a> &middot; 
    <a href="mailto:adhyatmasinghchauhan20031@gmail.com">Contact</a>
  </sub>
</p>
