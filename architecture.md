# Aptiv — Technical Architecture

> A multi-signal talent intelligence engine that ranks 100k+ candidates using skills, experience, behavioral indicators, risk-aware scoring, hidden potential detection, recruiter action prioritization, and narrative intelligence.

---

## Table of Contents

- [System Overview](#system-overview)
- [High-Level Architecture](#high-level-architecture)
- [Pipeline Stages](#pipeline-stages)
- [Module Descriptions](#module-descriptions)
  - [generate_submission.py — Orchestrator](#generate_submissionpy--orchestrator)
  - [candidate_parser.py — Feature Extraction Engine](#candidate_parserpy--feature-extraction-engine)
  - [scorer.py — Weighted Composite Scorer](#scorerpy--weighted-composite-scorer)
  - [hidden_gem_detector.py — Hidden Gem Detection](#hidden_gem_detectorpy--hidden-gem-detection)
  - [rap_engine.py — Recruiter Action Prioritization](#rap_enginepy--recruiter-action-prioritization)
  - [narrative_generator.py — Narrative Intelligence](#narrative_generatorpy--narrative-intelligence)
- [Data Schema & Input Formats](#data-schema--input-formats)
- [Feature Engineering Deep Dive](#feature-engineering-deep-dive)
- [Scoring Model Architecture](#scoring-model-architecture)
- [Hidden Gem Score Architecture](#hidden-gem-score-architecture)
- [RAP Score Architecture](#rap-score-architecture)
- [Narrative Intelligence Architecture](#narrative-intelligence-architecture)
- [Memory & Performance Design](#memory--performance-design)
- [Project Structure](#project-structure)
- [Dependency Graph](#dependency-graph)
- [Technology Stack](#technology-stack)
- [Design Decisions & Trade-offs](#design-decisions--trade-offs)
- [Extension Points](#extension-points)

---

## System Overview

Aptiv is a deterministic, rule-based candidate intelligence system designed for the Redrob Intelligent Candidate Discovery & Ranking Challenge. It processes 100,000 candidate profiles from raw JSON/JSONL data through a 6-stage pipeline: parsing → scoring → ranking → Hidden Gem detection → RAP → narrative generation. It outputs a ranked CSV submission and is designed for strict runtime (< 300s) and memory (< 16 GB) constraints.

The system is **stateless** (no database), **single-process** (no distributed compute), and **dependency-minimal** (only pandas + numpy for production).

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              APTIV PIPELINE (6 Stages)                          │
│                                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Input Data  │───▶│  Candidate   │───▶│   Scorer     │───▶│    Rank &     │  │
│  │  JSON/JSONL  │    │  Parser      │    │   (5 sub-    │    │    Sort       │  │
│  │              │    │  (~60 cols)  │    │   scores +   │    │               │  │
│  │              │    │              │    │   penalty)   │    │               │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────┬───────┘  │
│                                                                      │          │
│                                                                      ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │  Narrative   │◀───│     RAP      │◀───│      Hidden Gem Detector        │   │
│  │  Generator   │    │  (4-component│    │  (6-component HG score +        │   │
│  │  (archetype  │    │   score +    │    │   5 categories + narrative)     │   │
│  │  + tier +    │    │   priority)  │    │                                 │   │
│  │  narrative)  │    │              │    │                                 │   │
│  └──────┬───────┘    └──────────────┘    └─────────────────────────────────┘   │
│         │                                                                      │
│         ▼                                                                      │
│  ┌──────────────┐                                                              │
│  │  Submission  │                                                              │
│  │  CSV Export  │                                                              │
│  └──────────────┘                                                              │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

```
Stage 1: INGEST          Stage 2: PARSE           Stage 3: SCORE          Stage 4: MINE
─────────────────        ─────────────────        ─────────────────       ─────────────────
 .json ─┐                Line-by-line             5 weighted sub-         Hidden Gem score
         ├─▶ .jsonl ───▶  streaming parse   ───▶  score computation ──▶  (6 components)
 .jsonl ─┘               + post-processing        + risk penalty         + category assign
                          (recency, dupes)         clipped [0.0, 1.0]    + HG narrative

Stage 5: PRIORITIZE      Stage 6: NARRATE         Stage 7: EXPORT
─────────────────        ─────────────────        ─────────────────
 Engagement Velocity     Archetype detect         Sort by final_score
 Availability            Tier assignment          Assign ranks 1..N
 Conversion Likelihood   Strength synthesis       Write CSV
 Match Baseline          Risk synthesis
 RAP score → priority    Narrative composition
```

---

## Module Descriptions

### `generate_submission.py` — Orchestrator

| Aspect | Detail |
|--------|--------|
| **Role** | Main entry point; orchestrates the full 6-stage pipeline |
| **Entry** | `main()` via CLI with argparse |
| **Key Functions** | `run_pipeline()`, `load_json_candidates()`, `write_jsonl()`, `validate_dataframe()` |
| **Error Handling** | Validates DataFrame at each stage (non-empty, required columns); fails fast |
| **Logging** | Structured logging with timestamps and stage-level timing |
| **Cleanup** | Auto-removes temporary JSONL files after pipeline completion |

**CLI Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | `data/sample_candidates.json` | Input file path (.json or .jsonl) |
| `--output` | `submission.csv` | Output CSV path |
| `--temp-jsonl` | `data/temp_candidates.jsonl` | Temp JSONL for JSON-to-JSONL conversion |
| `--top-k` | `20` | Top candidates to display in console output |

**Pipeline Sequence:**
1. `parse_jsonl()` → scored DataFrame
2. `CandidateScorer.score_dataframe()` → adds sub-scores + `final_score`
3. Sort by `final_score` descending → assign `rank`
4. `detect_hidden_gems()` → adds HG columns
5. `compute_rap()` → adds RAP columns
6. `generate_candidate_narratives()` → adds narrative columns
7. Export `submission.csv` with `[candidate_id, rank, score]`

---

### `candidate_parser.py` — Feature Extraction Engine

| Aspect | Detail |
|--------|--------|
| **Role** | Extracts ~60 flat features from raw candidate JSON profiles |
| **Class** | `CandidateParser` — stateful (tracks seen names for duplicate detection) |
| **Entry** | `parse_jsonl(file_path)` — module-level function |
| **Pattern** | Streaming parse (line-by-line JSONL) → post-processing → DataFrame with dtype optimization |

**Internal Constants:**
- `SKILL_KEYWORDS` — Dict of 9 skill categories with keyword lists
- `ACRONYMS` — Set of short keywords requiring word-boundary matching (`\b`)
- `CONSULTING_COMPANIES` — Known consulting firms for disqualification
- `RESEARCH_WORDS` / `ENGINEERING_WORDS` — Title classification sets
- `CV_SPEECH_ROBOTICS_KEYWORDS` / `NLP_IR_KEYWORDS` — Domain mismatch detection

**Core Methods:**

| Method | Purpose |
|--------|---------|
| `extract_flat_features(cand)` | Main extraction: skills, disqualifiers, signals, flags |
| `_check_only_consulting(history)` | All roles at known consulting firms? |
| `_check_pure_research(history)` | All roles academic/research without engineering titles? |
| `_check_inactive_coder(history)` | Current role management >18 months without hands-on keywords? |
| `_check_title_chaser(history)` | Average tenure <18 months across 3+ roles? |
| `_check_domain_mismatch(skills, text)` | CV/Speech/Robotics skills without NLP/IR overlap? |

---

### `scorer.py` — Weighted Composite Scorer

| Aspect | Detail |
|--------|--------|
| **Role** | Computes a weighted composite relevance score |
| **Class** | `CandidateScorer` — stateless, configurable weights |
| **Design** | Fully vectorized NumPy/Pandas operations |

**Sub-score Methods:**

| Method | Weight | Key Logic |
|--------|--------|-----------|
| `compute_skill_match_score()` | 0.40 | 70% mandatory + 30% preferred skill fractions |
| `compute_production_experience_score()` | 0.25 | YoE/8 capped at 1.0; penalized for research (0.1×) or consulting (0.7×) |
| `compute_retrieval_ranking_experience_score()` | 0.15 | Binary vector_db (0.4) + embeddings (0.4) + nlp_ir (0.2) |
| `compute_behavioral_score()` | 0.10 | Response rate (40%) + recency (30%) + interview (20%) + open-to-work (10%) |
| `compute_startup_fit_score()` | 0.10 | Base 1.0; penalized for title chasing (-0.5) and consulting (-0.4) |
| `compute_risk_penalty()` | — | Chronology error (-0.3) + salary error (-0.3) + trust error (-0.2) |

> Note: `flag_duplicate_identity` is excluded from risk penalties. It is a synthetic dataset artifact (name collisions from repeated sampling) retained for informational reporting only.

---

### `hidden_gem_detector.py` — Hidden Gem Detection

| Aspect | Detail |
|--------|--------|
| **Role** | Identifies candidates whose potential is undervalued by keyword-based ranking |
| **Entry** | `detect_hidden_gems(df)` — module-level function |
| **Design** | Deterministic, rule-based, fully vectorized |

**Hidden Gem Score (0-100):**

| Component | Points | Signals |
|-----------|--------|---------|
| Behavioral Excellence | 30 | `score_behavioral` (response rate, recency, interview completion, open-to-work) |
| Skill Adjacency | 20 | Peaks near `score_skill_match ≈ 0.4` — adjacent skills, not perfect keyword overlap |
| Technical Evidence | 20 | GitHub activity + platform skill assessments (2+ scores ≥ 70) |
| Growth Trajectory | 15 | `score_startup_fit` (startup-friendly profile signals) |
| Market Demand | 10 | Profile views + recruiter saves (log-scaled normalization) |
| Recruitability | 5 | Open to work + willing to relocate |

**Threshold:** HG Score ≥ 60 → classified as Hidden Gem.

**Mutually Exclusive Categories (first-match wins):**

| Category | Criteria |
|----------|----------|
| Emerging Specialist | Skill assessments ≥ 2 scores ≥ 70 + ≤ 4 JD skill matches |
| Growth Candidate | 2-5yr experience + behavioral ≥ 0.75 + startup fit ≥ 0.7 |
| High Intent Candidate | Open to work + response rate ≥ 0.8 + interview rate ≥ 0.8 + active ≤ 30 days |
| Underexposed Expert | Skill match ≥ 0.5 + views+saves < 10 + GitHub ≥ 50 |
| Startup Builder | Startup fit ≥ 0.8 + distributed systems + GitHub ≥ 50 + relocate |

Each Hidden Gem receives a tailored 2-3 sentence recruiter briefing and a summary context line.

---

### `rap_engine.py` — Recruiter Action Prioritization

| Aspect | Detail |
|--------|--------|
| **Role** | Answers "Who should I contact first?" for a recruiter |
| **Entry** | `compute_rap(df)` — module-level function |
| **Design** | Deterministic, 4-component weighted score, threshold-based priority |

**RAP Score (0-100):**

| Component | Points | Sub-signals |
|-----------|--------|-------------|
| Engagement Velocity | 35 | Response rate (40%), response speed (25%), interview rate (20%), recency (15%) |
| Availability | 25 | Open to work (40%), notice period (35%), relocation (15%), work mode (10%) |
| Conversion Likelihood | 20 | Offer acceptance (35%), interview rate (25%), GitHub (20%), profile completeness (20%) |
| Match Baseline | 20 | `final_score` capped × 20 |

**Priority Thresholds:**
- ≥ 80 → **Contact Immediately** — Message NOW
- ≥ 65 → **Priority Outreach** — Send message within 24 hours
- ≥ 45 → **Standard Outreach** — Add to outreach queue this week
- ≥ 25 → **Long-Term Nurture** — Reassess in 30-60 days
- < 25 → **Do Not Prioritize**

Each candidate receives a `rap_score`, `rap_priority`, `rap_action` (one-line instruction with signal details), and `rap_rationale` (one-sentence explanation).

---

### `narrative_generator.py` — Narrative Intelligence

| Aspect | Detail |
|--------|--------|
| **Role** | Generates deterministic recruiter-facing candidate briefings |
| **Entry** | `generate_candidate_narratives(df)` — module-level function |
| **Template System** | 5 sets of 4-5 templates each, selected via `candidate_id` hash |

**7 Candidate Archetypes (detected in order):**

| Archetype | Detection Logic |
|-----------|----------------|
| Strong Fit — Verify First | `score ≥ 0.5` + has chronology/salary/trust flags |
| Leadership-Oriented | Inactive coder OR management title + ≥ 6yr experience |
| Production Retrieval Specialist | Vector DB + embeddings + ≥ 4yr experience |
| Deep Technical Specialist | ≥ 5 JD skill matches OR distributed systems |
| Startup Builder | Startup fit ≥ 0.8 + ≥ 2yr + not consulting-only |
| High-Engagement Candidate | Response rate ≥ 0.8 + open to work |
| Growth Candidate | < 4yr experience OR GitHub ≥ 0.6 |

**5 Tiers (based on final_score rank centiles):**
- Tier 1: Interview Immediately (top 2%)
- Tier 2: Strong Pipeline (2-10%)
- Tier 3: Worth a Screen (10-25%)
- Tier 4: Backup Pool (25-75%)
- Tier 5: Not Recommended (bottom 25% or score < 0.1)

**Narrative composition:**
- Section A: Thesis template + archetype + strengths synthesis
- Section B: Differentiation template + behavioral interpretation
- Section C: Verification items (risks, notice period, salary) or standard check
- Section D: Next-step action based on tier + risk profile

---

## Data Schema & Input Formats

### Supported Input Formats

| Format | Extension | Loading Strategy |
|--------|-----------|------------------|
| JSON Array | `.json` | Full load → convert to temp JSONL → stream parse |
| JSON Lines | `.jsonl` | Direct streaming parse (memory efficient) |

### Output Schema

```csv
candidate_id,rank,score
CAND_0000001,1,0.986533
CAND_0000042,2,0.982033
...
```

Internal DataFrame retains all enriched columns: sub-scores, archetype, narrative fields, HG score/category/narrative, RAP score/priority/action/rationale.

---

## Feature Engineering Deep Dive

### Skill Matching System

The parser performs keyword-based matching across **9 skill categories** using a two-source strategy:
1. **Skills list** — from `skills[].name` field
2. **Full text** — concatenation of `headline`, `summary`, and all `career_history[].description`

**Matching Logic:**
- **Standard keywords**: Substring match (`kw in text_lower`)
- **Acronyms** (`ndcg`, `mrr`, `map`, `ltr`, `nlp`, `ir`): Word-boundary regex (`\b...\b`) to prevent false positives

**Skill Categories:**

| Category | Priority | Example Keywords |
|----------|----------|------------------|
| `vector_db` | Mandatory | pinecone, weaviate, qdrant, milvus, faiss |
| `embeddings` | Mandatory | sentence-transformers, bge, e5, dense retrieval |
| `evaluation` | Mandatory | ndcg, mrr, map, a/b test |
| `python` | Mandatory | python |
| `llm_finetune` | Preferred | lora, qlora, peft, fine-tune |
| `learning_to_rank` | Preferred | xgboost, lightgbm, ltr |
| `nlp_ir` | Preferred | nlp, information retrieval, rag, search |
| `distributed_systems` | Preferred | ray, spark, triton, onnx, kubernetes |
| `hr_tech` | Bonus | hr-tech, talent intelligence, marketplace |

### Disqualification Heuristics

| Flag | Logic | Score Impact |
|------|-------|-------------|
| `disq_only_consulting` | All roles at consulting firms | Production exp × 0.7; startup fit -0.4 |
| `disq_pure_research` | All roles academic without engineering titles | Production exp × 0.1 |
| `disq_inactive_coder` | Management >18mo without hands-on keywords | Informational |
| `disq_title_chaser` | Avg tenure <18mo across 3+ roles | Startup fit -0.5 |
| `disq_domain_mismatch` | CV/Speech/Robotics without NLP/IR | Informational |

### Behavioral Signals

Extracted from `redrob_signals` with type-safe defaults. Includes response rate, response time, GitHub activity, interview completion, offer acceptance, notice period, relocation, work mode, salary expectations, and 7 additional signals for Hidden Gem detection (profile views, saves, search appearances, connections, endorsements, skill assessments, applications).

### Data Quality Flags

| Flag | Detection Rule | Risk Penalty |
|------|---------------|-------------|
| `flag_chronology_error` | `last_active_date < signup_date` | -0.3 |
| `flag_salary_error` | `expected_salary_max < expected_salary_min` | -0.3 |
| `flag_trust_error` | No verified email, phone, or LinkedIn | -0.2 |
| `flag_duplicate_identity` | Shared `anonymized_name` across profiles | **Informational only** (synthetic artifact) |
| `is_suspicious_profile` | Any of the above flags are True | Composite flag |

---

## Scoring Model Architecture

```
final_score = weighted_sum − risk_penalty, clipped to [0.0, 1.0]

weighted_sum =
  0.40 × skill_match
+ 0.25 × production_experience
+ 0.15 × retrieval_ranking
+ 0.10 × behavioral
+ 0.10 × startup_fit

risk_penalty =
  0.3 × chronology_error
+ 0.3 × salary_error
+ 0.2 × trust_error
```

All sub-scores are inherently bounded to [0.0, 1.0]. No global normalization applied.

---

## Hidden Gem Score Architecture

```
hg_score =
  30%  × behavioral_excellence
+ 20%  × skill_adjacency (peaks at 0.4 skill_match)
+ 20%  × technical_evidence (GitHub + assessments)
+ 15%  × growth_trajectory (startup_fit)
+ 10%  × market_demand (views + saves, log-scaled)
+  5%  × recruitability (open_to_work + relocate)
```

HG Score ≥ 60 → classified as Hidden Gem → assigned to first-matching category → generates narrative.

---

## RAP Score Architecture

```
rap_score =
  engagement_velocity  (35 pts max)
+ availability          (25 pts max)
+ conversion_likelihood (20 pts max)
+ match_baseline        (20 pts max)
```

Each component is a weighted composite of 3-4 sub-signals. Final score clipped to [0, 100]. Thresholds determine priority tier.

---

## Narrative Intelligence Architecture

1. **Archetype detection** — 7 mutually exclusive archetypes via rule cascade
2. **Tier assignment** — Based on final_score rank centiles
3. **Strength synthesis** — Skill/experience/behavior signals → natural language clauses
4. **Risk synthesis** — High-priority risks (chronology, salary, trust, inactivity, low response) → separate from low-priority (title chasing, domain mismatch, notice period)
5. **Recruitability extraction** — Notice period, relocation, salary expectations
6. **Template composition** — Deterministic template selection via candidate_id hash → 4-section narrative

---

## Memory & Performance Design

### Constraints vs Actual

| Metric | Target | Achieved |
|--------|--------|----------|
| Total pipeline (100k) | < 300s | 211s ✅ |
| Peak memory | < 16 GB | 284 MB ✅ |

### Stage Timings

| Stage | Time (s) |
|-------|----------|
| Parsing | 110.6 |
| Scoring | 0.2 |
| Hidden Gem Detection | 14.8 |
| RAP Computation | 31.9 |
| Narrative Generation | 46.7 |
| Export + Overhead | 7.0 |
| **Total** | **211.1** |

### Optimization Strategies

1. **Streaming Parse** — JSONL line-by-line; raw JSON discarded immediately
2. **Two-Pass Design** — First pass extracts features; second pass computes relative metrics
3. **DataFrame Dtype Optimization** — bool/int32/float32 dtypes reduce memory
4. **Vectorized Scoring** — All scoring uses NumPy/Pandas vectorized operations
5. **Zero External Dependencies for Benchmarking** — Windows `ctypes`/`psapi.dll` (avoids psutil)
6. **Temporary File Cleanup** — JSON-to-JSONL temp files auto-deleted

---

## Project Structure

```
Aptiv/
├── generate_submission.py      # Pipeline orchestrator (CLI entry)
├── candidate_parser.py         # Feature extraction engine
├── scorer.py                   # Weighted scoring model
├── narrative_generator.py      # Narrative intelligence + archetypes
├── hidden_gem_detector.py      # Hidden Gem detection
├── rap_engine.py               # Recruiter Action Prioritization
├── benchmark_parser.py         # Performance benchmarking utility
├── EDA.ipynb                   # Exploratory data analysis notebook
├── README.md                   # Project overview + usage guide
├── architecture.md             # This file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusion rules
└── data/
    ├── sample_candidates.json  # 50-candidate demo dataset
    ├── candidates.jsonl        # 100,000 candidates (full dataset, ~465 MB)
    ├── candidate_schema.json   # JSON schema reference
    ├── job_description.docx    # Job specification
    └── redrob_signals_doc.docx # Redrob signals documentation
```

---

## Dependency Graph

```
generate_submission.py
├── candidate_parser.py
│   ├── json           (stdlib)
│   ├── re             (stdlib)
│   ├── datetime       (stdlib)
│   ├── pandas
│   └── numpy
├── scorer.py
│   ├── pandas
│   └── numpy
├── hidden_gem_detector.py
│   ├── pandas
│   └── numpy
├── rap_engine.py
│   ├── pandas
│   └── numpy
├── narrative_generator.py
│   ├── pandas
│   └── numpy
└── (stdlib: json, time, logging, argparse, sys, pathlib)

benchmark_parser.py
├── candidate_parser.py
├── json, time, os      (stdlib)
├── ctypes              (stdlib, Windows)
└── pandas

EDA.ipynb
├── pandas
├── numpy
├── matplotlib
├── seaborn
├── scipy
└── scikit-learn
```

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 2.3.1 | DataFrame operations, CSV I/O |
| numpy | 2.1.3 | Vectorized numeric computation |

### Development Dependencies (EDA only)
- scikit-learn, scipy, matplotlib, seaborn (not required for pipeline execution)

---

## Design Decisions & Trade-offs

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Rule-based scoring over ML model** | Deterministic, explainable, no training data needed | Less adaptive; weights manually tuned |
| **JSONL streaming over bulk JSON load** | Memory efficient for 100k+ records | Requires JSON→JSONL conversion for JSON input |
| **Substring matching over embeddings** | Zero model inference cost; 211s for 100k | May miss semantic similarity |
| **Word-boundary regex for acronyms** | Prevents false positives ("map" in "mapping") | Slightly slower for those keywords |
| **Single-process pipeline** | Simplicity; meets <300s easily | Cannot leverage multi-core |
| **Windows-specific memory tracking** | Avoids psutil dependency | Benchmark only works on Windows |
| **No persistent storage** | Reproducible from raw data | Must re-parse every run |
| **Hardcoded skill keywords** | Tailored to specific JD | Not generalizable without code changes |
| **Template-based narratives** | Deterministic, auditable, no LLM cost | Less natural than generative LLM |
| **HG/RAP as post-scoring stages** | Each measures a different dimension | Adds 93s to total runtime |

---

## Extension Points

| Extension | Where to Modify | Complexity |
|-----------|----------------|------------|
| Add new skill categories | `SKILL_KEYWORDS` dict in `candidate_parser.py` | Low |
| Adjust scoring weights | `CandidateScorer.__init__()` weights dict | Low |
| Add new disqualification rules | New `_check_*` method in `CandidateParser` | Low |
| Configurable weights via YAML/JSON | Load in `generate_submission.py` | Medium |
| Explainability (SHAP) | Post-scoring analysis | Medium |
| Semantic skill matching | Replace `search_keywords()` with embeddings | High |
| Incremental scoring | Refactor `score_dataframe()` to batch mode | High |
| REST API serving | Wrap pipeline in FastAPI | Medium |
| Docker containerization | Add Dockerfile | Low |
| Unit test suite | Add `tests/` directory with pytest | Medium |
