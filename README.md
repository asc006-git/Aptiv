# Aptiv

A multi-signal talent intelligence engine that ranks candidates using skills, experience, behavioral indicators, risk-aware scoring, hidden potential detection, recruiter action prioritization, and narrative intelligence.

---

## Project Overview

Aptiv is an intelligent candidate discovery and ranking system built for the Redrob Intelligent Candidate Discovery & Ranking Challenge. It processes 100,000 candidate profiles, extracts ~60 structured features per candidate, computes a weighted multi-factor relevance score, detects Hidden Gems that keyword ranking would miss, prioritizes recruiter actions via RAP scoring, and generates human-readable candidate narratives — all within strict runtime (< 300s) and memory (< 16 GB) constraints.

---

## Problem Statement

Given a dataset of 100,000 candidate profiles containing professional profiles, career history, and Redrob platform behavioral signals, rank candidates by relevance to a Senior ML Engineer — RAG & Search role emphasizing:

- Vector database expertise (Pinecone, Weaviate, Qdrant, Milvus, Faiss)
- Embeddings & dense retrieval (sentence-transformers, BGE, E5)
- Ranking evaluation (NDCG, MRR, MAP, offline-to-online)
- Python proficiency
- LLM fine-tuning (LoRA, QLoRA, PEFT)
- Learning-to-rank (XGBoost, LightGBM)
- Distributed systems (Ray, Spark, Triton, ONNX)
- NLP / Information Retrieval background

---

## Pipeline Architecture

```
Dataset (JSON/JSONL)
    ↓
candidate_parser.py    — Streaming parse → ~60 flat features + honeypot flags
    ↓
scorer.py              — 5 weighted sub-scores + risk penalty (incl. honeypot) → final_score [0,1]
    ↓
Ranking                — Sort by final_score DESC, candidate_id ASC → rank 1..N
    ↓
hidden_gem_detector.py — 6-component HG score → 5 categories + narrative
    ↓
rap_engine.py          — 4-component RAP score → priority + action + rationale
    ↓
narrative_generator.py — Archetype + tier + strength/risk synthesis → narrative
    ↓
submission.csv         — Top 100: candidate_id, rank, score, reasoning
```

---

## Capabilities

### 1. Candidate Parser (`candidate_parser.py`)
Streaming JSONL parser extracting ~60 features per candidate:
- **Skill Matching** — 9 keyword categories across skills + full-text (with word-boundary regex for acronyms)
- **Disqualification Heuristics** — 5 rule-based checks (consulting-only, pure research, title chaser, inactive coder, domain mismatch)
- **Behavioral Signals** — Response rates, activity recency, interview completion, GitHub activity, salary expectations
- **Data Quality Flags** — Chronology errors, salary errors, trust errors, duplicate identity (informational)

### 2. Ranking Engine (`scorer.py`)
Weighted composite scoring with 5 components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Skill Match | 0.40 | 70% mandatory skills (vector DB, embeddings, eval, Python) + 30% preferred (LLM fine-tune, LTR, distributed, NLP/IR) |
| Production Experience | 0.25 | YoE / 8 capped at 1.0; penalized for research (0.1×) or consulting-only (0.7×) |
| Retrieval/Ranking Experience | 0.15 | Binary signals: vector DB (0.4) + embeddings (0.4) + NLP/IR (0.2) |
| Behavioral | 0.10 | Response rate (40%) + recency (30%) + interview completion (20%) + open-to-work (10%) |
| Startup Fit | 0.10 | Base 1.0; penalized for title chasing (-0.5) or consulting-only (-0.4) |

**Risk Penalty:** Chronology error (-0.3) + Salary error (-0.3) + Trust error (-0.2).  
**Final Score:** `weighted_sum - risk_penalty`, clipped to [0.0, 1.0].  
*Note: `flag_duplicate_identity` is excluded from scoring penalties — it is a synthetic dataset artifact retained for informational reporting only.*

### 3. Hidden Gem Detection (`hidden_gem_detector.py`)
Identifies candidates that keyword-based ranking would undervalue, using a 6-component score (0-100):

| Component | Weight | What It Measures |
|-----------|--------|-----------------|
| Behavioral Excellence | 30% | Response rate, recency, interview completion |
| Skill Adjacency | 20% | Peaks near 0.4 skill match — adjacent skills, not perfect keyword overlap |
| Technical Evidence | 20% | GitHub activity + platform skill assessments |
| Growth Trajectory | 15% | Startup fit score |
| Market Demand | 10% | Profile views + recruiter saves (log-scaled) |
| Recruitability | 5% | Open to work + willing to relocate |

Candidates scoring ≥ 60 are classified into 5 categories: **Emerging Specialist**, **Growth Candidate**, **High Intent Candidate**, **Underexposed Expert**, **Startup Builder** — each with a tailored recruiter briefing.

### 4. Recruiter Action Prioritization — RAP (`rap_engine.py`)
Answers "Who should I contact first?" with a 0-100 score across 4 components:

| Component | Points | Signals |
|-----------|--------|---------|
| Engagement Velocity | 35 | Response rate, response speed, interview rate, recency |
| Availability | 25 | Open to work, notice period, relocation, work mode |
| Conversion Likelihood | 20 | Offer acceptance, interview rate, GitHub, profile completeness |
| Match Baseline | 20 | Final score (capped) |

**Priority thresholds:** ≥80 Contact Immediately · ≥65 Priority Outreach · ≥45 Standard Outreach · ≥25 Long-Term Nurture · <25 Do Not Prioritize.

Each candidate receives a priority label, a specific recruiter action instruction, and a one-sentence rationale.

### 5. Narrative Intelligence (`narrative_generator.py`)
Generates deterministic, recruiter-facing candidate briefings with:

- **7 Archetypes** — Strong Fit, Leadership-Oriented, Production Retrieval Specialist, Deep Technical Specialist, Startup Builder, High-Engagement Candidate, Growth Candidate
- **5 Tiers** — Interview Immediately (top 2%) through Not Recommended (bottom 25%)
- **Template Diversity** — 5 thesis templates, 5 differentiation templates, 4 verification templates, 4 next-step templates, 4 recruitability templates selected deterministically via candidate_id hash
- **Section A:** Why this candidate (archetype + strengths)
- **Section B:** What differentiates them (behavioral synthesis)
- **Section C:** What to verify (risks + notice + salary)
- **Section D:** Suggested action

### 6. Submission Generator (`generate_submission.py`)
CLI orchestrator that runs the full pipeline and outputs `submission.csv` with columns: `candidate_id, rank, score, reasoning` (top 100 only). Internal DataFrame retains all enriched columns (archetype, narrative, HG score, RAP score, etc.) for analysis and PPT material.

---

## Dataset Handling

### Input Formats
- **JSON** (`data/sample_candidates.json`) — Array of 50 candidate objects (quick demo)
- **JSONL** (`data/candidates.jsonl`) — Streaming format, 100k candidates, ~465 MB

### Output
- **`submission.csv`** — `candidate_id, rank, score, reasoning` (top 100 rows, ~0.1 MB)

---

## Usage

### Dependencies
```bash
pip install -r requirements.txt
```

### Quick Start (50 candidates)
```bash
python generate_submission.py
```

### Full Dataset (100k candidates)
```bash
python generate_submission.py --input data/candidates.jsonl --output submission.csv
```

### Options
```bash
python generate_submission.py --help
```
| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | `data/sample_candidates.json` | Input file (.json or .jsonl) |
| `--output` | `submission.csv` | Output CSV path |
| `--temp-jsonl` | `data/temp_candidates.jsonl` | Temp file for JSON input |
| `--top-k` | `20` | Number of top candidates to display |

---

## Benchmark Results (100k candidates)

| Stage | Time | % of Total |
|-------|------|------------|
| Parsing | 170.7s | 65.3% |
| Scoring | 0.2s | 0.1% |
| Hidden Gem Detection | 18.3s | 7.0% |
| RAP Computation | 39.2s | 15.0% |
| Narrative Generation | 30.7s | 11.7% |
| Export + Overhead | 2.3s | 0.9% |
| **Total Pipeline** | **261.5s** | 100% |

| Metric | Result | Constraint |
|--------|--------|------------|
| Total runtime | 261 seconds | < 300 seconds ✅ |
| Peak memory (DataFrame) | 285 MB | < 16 GB ✅ |
| Candidates processed | 100,000 | — |
| Output format | `candidate_id, rank, score, reasoning` (top 100) | ✅ |
| Validator passes | Yes | ✅ |
| Honeypots in top 100 | 0 / 100 (0%) | < 10% ✅ |

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
├── EDA.ipynb                   # Exploratory data analysis
├── README.md                   # This file
├── architecture.md             # Technical architecture deep-dive
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusion rules
└── data/
    ├── sample_candidates.json  # 50-candidate demo dataset
    ├── candidates.jsonl        # 100,000 candidates (full dataset)
    ├── candidate_schema.json   # JSON schema reference
    ├── job_description.docx    # Job specification
    └── redrob_signals_doc.docx # Redrob signals documentation
```

---

## Future Improvements

- [ ] Incremental / streaming scoring for datasets >1M candidates
- [ ] Configurable weight profiles via YAML/JSON
- [ ] Explainability layer (SHAP values per candidate)
- [ ] A/B testing framework for weight optimization
- [ ] Integration with Redrob API for real-time signals
- [ ] Support for custom disqualification rules
- [ ] Docker containerization for deployment
- [ ] Unit test suite
