# Aptiv

AI-powered Talent Intelligence Platform that ranks, explains, and prioritizes 100,000 candidates against any technical role using multi-factor relevance scoring, Hidden Gem detection, Recruiter Action Prioritization (RAP), and deterministic narrative intelligence — all within 200 seconds on a single CPU core.

---

## Problem Statement

Traditional applicant tracking systems (ATS) rely on keyword matching — counting resume hits against a job description. This approach systematically undervalues three categories of candidates:

1. **Adjacent-skill candidates** whose keyword count is moderate but whose underlying capabilities map directly to the role's core function (e.g., an NLP researcher who has built search pipelines but never used Pinecone by name)
2. **High-intent, high-availability candidates** who are responsive, interview well, and can start quickly but whose resumes lack perfect keyword overlap
3. **Underexposed experts** with strong technical signals (GitHub activity, skill assessments) but low recruiter visibility or platform engagement

Aptiv solves this by modeling candidate quality across five independent dimensions — skill match, production experience, retrieval/ranking depth, behavioral engagement, and startup fit — then layering risk penalties, Hidden Gem detection, and recruiter action prioritization on top. The result is a ranking that captures genuine capability, not just keyword density.

---

## Key Features

| Feature | Description |
|---|---|
| **Multi-factor Candidate Ranking** | 5-component weighted scoring (skill match 0.40, production experience 0.25, retrieval/ranking 0.15, behavioral 0.10, startup fit 0.10) with risk penalties for data quality and honeypot inconsistencies. Final score [0, 1]. |
| **Hidden Gem Detection** | 6-component score (behavioral excellence, skill adjacency, technical evidence, growth trajectory, market demand, recruitability) classifying candidates into 5 undervalued categories. |
| **Recruiter Action Prioritization (RAP)** | 4-component urgency score (engagement velocity, availability, conversion likelihood, match baseline) mapping to 5 outreach priorities from "Contact Immediately" to "Do Not Prioritize." |
| **Explainable AI Ranking** | Score breakdown by sub-component, pool-relative percentile ranking, JD alignment markers, strength/risk decomposition — every score is audit-able and recruiter-interpretable. |
| **Narrative Intelligence** | Deterministic, hash-varied candidate briefings with 10 recruiter archetypes, 5 rank-based tiers, 8 distinct structural templates, and candidate-specific signal injection. Zero LLM calls. |
| **Sandbox Interface** | Streamlit-based interactive platform: upload candidate data, run ranking, explore leaderboard, Hidden Gems, and RAP analysis, export results. |
| **Submission-Compliant CSV Generation** | Single-command pipeline outputs `candidate_id, rank, score, reasoning` for top 100 candidates. Validator-compliant, deterministic, reproducible. |

---

## System Architecture

```
candidates.jsonl / sample_candidates.json
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  candidate_parser.py                                                 │
│  Streaming JSONL parser extracting ~60 structured features per       │
│  candidate: skill keywords (9 categories, word-boundary regex for    │
│  acronyms), disqualification heuristics (5 rules), behavioral        │
│  signals (response rates, recency, interview completion, GitHub,     │
│  salary expectations), data quality flags (chronology, salary,       │
│  trust, honeypot inconsistencies).                                   │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  scorer.py                                                           │
│  Weighted composite scoring across 5 dimensions. Mandatory skills    │
│  (vector DBs, embeddings, evaluation, Python) weighted 70% within    │
│  skill match; preferred (LLM fine-tuning, learning-to-rank,          │
│  distributed systems, NLP/IR) weighted 30%. Production experience    │
│  capped at 8 YoE with penalties for pure research (0.1×) or          │
│  consulting-only (0.7×). Retrieval/ranking score from binary         │
│  signals. Behavioral score from response rate, recency, interview    │
│  completion, and open-to-work. Startup fit penalized for title-      │
│  chasers and consulting-only profiles. Risk penalty subtracts for    │
│  chronology errors (-0.3), salary errors (-0.3), trust errors       │
│  (-0.2), and honeypot flags (-0.3 each).                             │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  hidden_gem_detector.py                                              │
│  6-component Hidden Gem score (0-100) identifying undervalued        │
│  candidates. Components: behavioral excellence (30%), skill          │
│  adjacency — peaks near 0.4 skill match, not perfect overlap (20%),  │
│  technical evidence via GitHub + assessments (20%), growth           │
│  trajectory via startup fit (15%), market demand via profile views + │
│  saves, log-scaled (10%), recruitability — open-to-work + relocation │
│  (5%). Threshold ≥ 60 → 5 mutually exclusive categories.            │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  rap_engine.py                                                       │
│  Recruiter Action Prioritization (0-100). Four components:           │
│  engagement velocity (35 pts): response rate, response speed,        │
│  interview rate, recency; availability (25 pts): open-to-work,       │
│  notice period, relocation, work-mode flexibility; conversion        │
│  likelihood (20 pts): offer acceptance rate, interview rate, GitHub  │
│  activity, profile completeness; match baseline (20 pts): final      │
│  score capped. Maps to 5 priorities from "Contact Immediately"       │
│  (≥80) to "Do Not Prioritize" (<25).                                │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  narrative_generator.py                                              │
│  Deterministic, recruiter-facing candidate briefings. Assigns 10     │
│  archetypes (Production Veteran, Recruiter Favorite, Growth          │
│  Candidate, Emerging Specialist, Startup Builder, Passive Expert,    │
│  High Risk/High Reward, Hidden Gem, Product-Minded Engineer,         │
│  High Conviction Hire) via scored rule system. 5 rank-based tiers    │
│  (Tier 1: Interview Immediately through Tier 5: Not Recommended).    │
│  8 structurally distinct narrative templates selected via            │
│  candidate_id hash — each template uses hash-varied phrasing from    │
│  12+ signal banks ensuring every narrative is unique. Every          │
│  narrative includes: JD alignment marker, score breakdown, pool-     │
│  relative percentile, strengths, concerns, recruiter action, and     │
│  next-step recommendation.                                           │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  generate_submission.py                                              │
│  CLI orchestrator: parse → score → rank → HG → RAP → narratives →   │
│  export. Single command processes 100K candidates. Outputs           │
│  submission CSV with columns candidate_id, rank, score, reasoning    │
│  (top 100). Internal DataFrame retains all enriched columns for      │
│  analysis. Validator-compliant. Deterministic and reproducible.      │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  app.py (Sandbox)                                                    │
│  Streamlit interactive platform. Upload sample data, run full        │
│  ranking pipeline, explore results through leaderboard view,         │
│  Hidden Gem cards, RAP priority table, and candidate detail panels.  │
│  Export ranked CSV, Hidden Gems CSV, RAP priorities CSV, and         │
│  recruiter shortlist CSV directly from the browser.                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Scoring Methodology

### Component Weights

| Component | Weight | Signals Measured |
|---|---|---|
| Skill Match | 0.40 | 70% mandatory (vector DBs, embeddings, evaluation, Python) + 30% preferred (LLM fine-tuning, learning-to-rank, distributed systems, NLP/IR) |
| Production Experience | 0.25 | Years of experience capped at 8; penalized for pure research (0.1×) or consulting-only (0.7×) |
| Retrieval / Ranking Experience | 0.15 | Binary: vector DB (0.4) + embeddings/dense retrieval (0.4) + NLP/IR (0.2) |
| Behavioral Score | 0.10 | Recruiter response rate (40%) + login recency (30%) + interview completion (20%) + open-to-work (10%) |
| Startup Fit | 0.10 | Base 1.0; penalized for title-chaser (-0.5) or consulting-only (-0.4) |

### Risk Penalties

| Flag | Penalty | Source |
|---|---|---|
| Chronology error | -0.30 | Employment timeline inconsistency |
| Salary error | -0.30 | Salary expectation out of range |
| Trust error | -0.20 | Known profile data quality issue |
| Honeypot: timeline inflated | -0.30 | Suspiciously rapid career progression |
| Honeypot: skill inflated | -0.30 | Unrealistic skill breadth |
| Honeypot: title mismatch | -0.30 | Title does not match experience |

**Final Score =** `0.40 × SkillMatch + 0.25 × ProdExp + 0.15 × RetrievalRank + 0.10 × Behavioral + 0.10 × StartupFit − RiskPenalty`, clipped to [0.0, 1.0].

### Honeypot Detection

The profile contains synthetic trap candidates with intentionally inflated timelines, broad skill claims, or title-to-experience mismatches. These are detected via heuristic rules during parsing and penalized in scoring. The `flag_duplicate_identity` signal (informational only) detects a synthetic dataset artifact — repeated name generation from a limited 50-name pool — and is explicitly excluded from scoring penalties.

---

## Hidden Gem Engine

Hidden Gems are candidates whose true potential is not reflected in their keyword-based rank. The engine computes a 0–100 score across 6 components and classifies candidates scoring ≥ 60 into 5 categories:

| Category | Detection Criteria | Recruiter Value |
|---|---|---|
| **Emerging Specialist** | Strong skill assessments but ≤ 4 JD keyword matches | Technical competence beyond resume keywords |
| **Growth Candidate** | 2–5 YoE, behavioral score ≥ 0.75, startup fit ≥ 0.7 | High ceiling, coachable, motivated |
| **High Intent Candidate** | Open to work, response rate ≥ 80%, interview rate ≥ 80%, active within 30 days | Ready to move, low friction to engage |
| **Underexposed Expert** | Skill match ≥ 0.5, low recruiter visibility (< 10 views + saves), GitHub ≥ 50 | Strong technical signals overlooked by the market |
| **Startup Builder** | Startup fit ≥ 0.8, distributed systems match, GitHub ≥ 50, willing to relocate | Full-stack ownership mentality |

Each category includes a tailored 2–3 sentence recruiter briefing explaining why the candidate is valuable despite their ranking position.

---

## Recruiter Action Prioritization (RAP)

RAP answers the recruiter's core question: *"Of these 100,000 candidates, who should I contact first?"* The score (0–100) is computed from 4 components:

| Component | Max Points | Key Signals |
|---|---|---|
| Engagement Velocity | 35 | Response rate, response speed (hrs), interview rate, login recency |
| Availability | 25 | Open to work, notice period, relocation willingness, work mode flexibility |
| Conversion Likelihood | 20 | Offer acceptance rate, interview rate, GitHub activity, profile completeness |
| Match Baseline | 20 | Final score (capped) |

### Priority Thresholds

| RAP Score | Priority | Implied Action |
|---|---|---|
| ≥ 80 | Contact Immediately | Reach out within 24 hours |
| 65–79 | Priority Outreach | Schedule screen this week |
| 45–64 | Standard Outreach | Add to active pipeline |
| 25–44 | Long-Term Nurture | Monitor for re-engagement |
| < 25 | Do Not Prioritize | Deprioritize in favor of higher-scoring candidates |

Each RAP assignment includes a specific action instruction (e.g., "Send personalized outreach referencing their vector DB experience") and a one-sentence rationale.

---

## Explainability Layer

Every ranking decision is accompanied by recruiter-interpretable justification:

- **Score breakdown** — Sub-component scores (skill match, production, retrieval, behavioral, startup fit) visible per candidate
- **Pool-relative percentile** — Where the candidate stands relative to the full 100K pool for each sub-score
- **JD alignment markers** — Specific JD phrases (founding-team fit, production-over-research preference) matched against candidate signals
- **Strength / risk decomposition** — Positive signals (keyword matches, GitHub activity, high response rate) and concerns (chronology errors, salary gaps, long notice periods) extracted and formatted
- **Narrative generation** — Full recruiter-facing briefing with archetype classification, tier assignment, differentiation text, verification probes, and next-step recommendation. All phrasing varies deterministically by candidate_id hash — no two narratives are identical.

---

## Sandbox Platform

The interactive Streamlit interface (`app.py`) provides:

| View | What It Shows |
|---|---|
| **Dataset Upload** | Drop a JSON/JSONL candidate file (or use the built-in 50-candidate sample) |
| **Ranking Pipeline** | Run the full parse → score → rank → HG → RAP → narratives pipeline with progress indicators |
| **Leaderboard** | Top 100 ranked candidates with score, archetype, tier, and expandable detail panels |
| **Hidden Gems** | Filtered view of all Hidden Gem candidates with category labels and recruiter briefings |
| **RAP Analysis** | Sorted by RAP score with priority labels, actions, and rationales |
| **Candidate Detail** | Per-candidate: score radar chart, sub-score breakdown, positive signals, concerns, full narrative |
| **Exports** | Ranked CSV, Hidden Gems CSV, RAP Priorities CSV, Recruiter Shortlist CSV — all with `candidate_id` as first column |

Deployed configuration: headless mode, CORS disabled, dark theme. Falls back to `data/sample_candidates.json` (50 candidates) when the full 465 MB `candidates.jsonl` is unavailable.

---

## Repository Structure

```
Aptiv/
├── app.py                          # Streamlit sandbox (interactive platform)
├── generate_submission.py          # CLI pipeline orchestrator
├── candidate_parser.py             # Feature extraction engine (~60 features)
├── scorer.py                       # Multi-factor weighted scoring
├── hidden_gem_detector.py          # Hidden Gem detection (6-component score)
├── rap_engine.py                   # Recruiter Action Prioritization
├── narrative_generator.py          # Narrative intelligence (10 archetypes)
├── requirements.txt                # Dependencies: streamlit, pandas, numpy
├── README.md                       # This file
├── submission_metadata.yaml        # Challenge metadata
├── .gitignore
├── .streamlit/
│   └── config.toml                 # Streamlit deployment configuration
└── data/
    ├── sample_candidates.json      # 50-candidate demo dataset
    ├── candidates.jsonl            # 100,000 candidates (full dataset, 465 MB, gitignored)
    ├── candidate_schema.json       # JSON schema reference
    ├── validate_submission.py      # Official submission validator
    ├── job_description.docx        # Challenge job specification
    └── redrob_signals_doc.docx     # Redrob behavioral signals documentation
```

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `streamlit`, `pandas`, `numpy`. No GPU, no LLM API keys, no external services required.

---

## Run Sandbox

```bash
streamlit run app.py
```

Opens the interactive ranking platform in your browser. Uses the 50-candidate sample by default; upload a custom JSON/JSONL file for full analysis.

---

## Generate Submission

### Full dataset (100,000 candidates)

```bash
python generate_submission.py --input data/candidates.jsonl --output Adhyatma_Singh_Chauhan.csv
```

### Quick demo (50 candidates)

```bash
python generate_submission.py
```

### CLI Options

| Argument | Default | Description |
|---|---|---|
| `--input` | `data/sample_candidates.json` | Input file (.json or .jsonl) |
| `--output` | `submission.csv` | Output CSV path |
| `--temp-jsonl` | `data/temp_candidates.jsonl` | Temp file for JSON→JSONL conversion |
| `--top-k` | `20` | Number of top candidates to display in console |

---

## Validation

```bash
python data/validate_submission.py Adhyatma_Singh_Chauhan.csv
```

Expected output: `Submission is valid.`

The validator checks: header format, 100-row count, `candidate_id` uniqueness, ID format compliance, source data existence, score range [0,1], monotonic ranking, tie-breaking order, and non-empty unique reasoning strings.

---

## Performance Benchmarks

Tested on 4-core CPU, 16 GB RAM, Windows 10 — no GPU, no network.

| Metric | Result |
|---|---|
| Total pipeline runtime (100K candidates) | ~199 seconds |
| Peak DataFrame memory | ~205 MB |
| Candidates processed | 100,000 |
| Features extracted per candidate | ~60 |
| Output rows (submission CSV) | 100 |
| Execution | Deterministic, CPU-only |
| Network dependency | None |

### Stage Breakdown

| Stage | Time | % of Total |
|---|---|---|
| Parsing | ~130s | 65% |
| Scoring | ~0.2s | <1% |
| Hidden Gem Detection | ~14s | 7% |
| RAP Computation | ~30s | 15% |
| Narrative Generation | ~23s | 12% |
| Export + Overhead | ~2s | 1% |

---

## Submission Compliance

| Requirement | Status |
|---|---|
| Validator compliance | ✅ PASS |
| Top 100 candidates | ✅ 100 rows |
| Score range [0, 1] | ✅ 0.8435–0.9865 |
| Monotonically non-increasing scores | ✅ Verified |
| Tie-breaking by candidate_id ASC | ✅ Verified |
| All candidate_ids unique | ✅ Verified |
| All candidate_ids exist in source | ✅ Verified |
| All reasoning non-empty | ✅ Verified |
| All reasoning unique (100/100) | ✅ Verified |
| Deterministic ranking | ✅ Same input → same output |
| Reproducible pipeline | ✅ Single command, no external dependencies |

---

## Future Enhancements

- **Real-time ATS integration** — Webhook-based ingestion from Greenhouse, Lever, Ashby for live candidate scoring as profiles enter the pipeline
- **LLM-assisted recruiter workflows** — Optional LLM enhancement for narrative refinement while keeping ranking deterministic
- **Talent graph analytics** — Cross-candidate relationship modeling (shared employers, schools, skill clusters) for team-building insights
- **Interview prediction models** — ML-based interview stage outcome prediction using RAP signals as features
- **Configurable weight profiles** — YAML/JSON-based weight configuration for different role families (ML Engineer, Product Manager, Designer)
- **Incremental scoring** — Streaming architecture for datasets exceeding 1M candidates without full reprocessing
- **Docker containerization** — Production-ready deployment with Docker + docker-compose for cloud-native environments

---

## About

Aptiv was built as an AI Talent Intelligence Platform — a system designed to surface the candidates that keyword-based filtering misses, explain why each ranking decision was made, and tell recruiters exactly who to contact first and why.
