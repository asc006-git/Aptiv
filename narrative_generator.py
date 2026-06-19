import pandas as pd
import numpy as np

# ── Rank-Based Display Tiers (for Top 100) ──────────────────────────
RANK_TIER_BOUNDS = [
    (1, 10, "Elite Match"),
    (11, 25, "Strong Match"),
    (26, 50, "Recommended"),
    (51, 75, "Potential Fit"),
    (76, 100, "Consider"),
]

def assign_display_tier(rank):
    for lo, hi, label in RANK_TIER_BOUNDS:
        if lo <= rank <= hi:
            return label
    return "Consider"

# ── Original tier logic (preserved for internal use) ────────────────

THESIS_TEMPLATES = [
    "Classified as a **{arch}** ({tier_short}), this candidate is positioned well due to their {strengths_text}.",
    "As a **{arch}** ({tier_short}), this candidate brings {strengths_text}.",
    "This **{arch}** ({tier_short}) stands out with {strengths_text}.",
    "Ranked as a **{arch}** ({tier_short}), the candidate demonstrates {strengths_text}.",
    "A **{arch}** ({tier_short}) profile, strengthened by {strengths_text}.",
]

DIFF_TEMPLATES = [
    "They stand out on the platform by being {behavior}.",
    "What differentiates them: {behavior}.",
    "Their platform presence shows {behavior}.",
    "Notable platform signals: {behavior}.",
    "A key differentiator is {behavior}.",
]

VERIFY_TEMPLATES_WITH_RISKS = [
    "The recruiter should prioritarily {items}.",
    "Immediate verification needed: {items}.",
    "Before proceeding, address: {items}.",
    "Recruiter must first {items}.",
]

VERIFY_TEMPLATES_NO_RISKS = [
    "Verification of notice period and standard background check is recommended.",
    "Standard background check and notice period verification advised.",
    "Recommend standard verification of notice period and background.",
    "Proceed with standard due diligence on notice period and background.",
]

NEXT_STEP_TEMPLATES = [
    "Suggested Action: **{act}** to initiate next steps.",
    "Recommended next step: **{act}**.",
    "Action: **{act}** to move forward.",
    "Proceed with: **{act}**.",
]

RECRUIT_TEMPLATES = [
    "Notice period is {notice} days; {relocate_text_title}{salary_clause}.",
    "Available in {notice} days, {relocate_text}{salary_clause}.",
    "They {relocate_text_subj} with a {notice}-day notice{salary_clause}.",
    "Notice: {notice} days. {relocate_text_title}{salary_clause}.",
]

# Deterministic template selector based on candidate_id hash
def _select_template(templates, candidate_id):
    """Select a template deterministically based on candidate_id."""
    try:
        idx = int(candidate_id.split('_')[-1]) % len(templates)
    except:
        idx = 0
    return templates[idx]


def assign_tiers(df):
    total_candidates = len(df)
    if total_candidates == 0:
        return pd.Series(dtype=str)
    tiers = np.empty(total_candidates, dtype=object)
    ranks = np.arange(1, total_candidates + 1)
    p2 = max(1, int(0.02 * total_candidates))
    p10 = max(1, int(0.10 * total_candidates))
    p25 = max(1, int(0.25 * total_candidates))
    p75 = max(1, int(0.75 * total_candidates))
    for i in range(total_candidates):
        score = df.iloc[i].get('final_score', 0.0)
        if score < 0.1:
            tiers[i] = "Tier 5 - Not Recommended"
            continue
        rank = ranks[i]
        if rank <= p2:
            tiers[i] = "Tier 1 - Interview Immediately"
        elif rank <= p10:
            tiers[i] = "Tier 2 - Strong Pipeline"
        elif rank <= p25:
            tiers[i] = "Tier 3 - Worth a Screen"
        elif rank <= p75:
            tiers[i] = "Tier 4 - Backup Pool"
        else:
            tiers[i] = "Tier 5 - Not Recommended"
    return pd.Series(tiers, index=df.index)


def detect_archetype(row, score):
    """Detects exactly one primary recruiter archetype for a candidate based on profile signals.
    
    Supported archetypes:
    - Strong Fit — Verify First
    - Leadership-Oriented
    - Production Retrieval Specialist
    - Deep Technical Specialist
    - Startup Builder
    - High-Engagement Candidate
    - Growth Candidate
    """
    yoe = row.get('years_of_experience', 0.0)
    title = str(row.get('current_title', '')).lower()
    
    # 1. Strong Fit — Verify First
    has_real_flags = row.get('flag_chronology_error', False) or row.get('flag_salary_error', False) or row.get('flag_trust_error', False)
    if has_real_flags and score >= 0.5:
        return "Strong Fit — Verify First"
        
    # 2. Leadership-Oriented
    is_mgmt = any(word in title for word in ['manager', 'director', 'head', 'architect', 'lead', 'chief', 'vp', 'cto'])
    if row.get('disq_inactive_coder', False) or (is_mgmt and yoe >= 6):
        return "Leadership-Oriented"
        
    # 3. Production Retrieval Specialist
    if row.get('match_vector_db', False) and row.get('match_embeddings', False) and yoe >= 4:
        return "Production Retrieval Specialist"
        
    # 4. Deep Technical Specialist
    if row.get('total_jd_skill_matches', 0) >= 5 or row.get('match_distributed_systems', False):
        return "Deep Technical Specialist"
        
    # 5. Startup Builder
    if row.get('score_startup_fit', 1.0) >= 0.8 and yoe >= 2 and not row.get('disq_only_consulting', False):
        return "Startup Builder"
        
    # 6. High-Engagement Candidate
    if row.get('recruiter_response_rate', 0.0) >= 0.8 and row.get('open_to_work_flag', False):
        return "High-Engagement Candidate"
        
    # 7. Growth Candidate
    if yoe < 4 or row.get('github_activity_score', 0.0) >= 0.6:
        return "Growth Candidate"
        
    # Default fallbacks
    if row.get('total_jd_skill_matches', 0) >= 3:
        return "Deep Technical Specialist"
    return "Startup Builder"


def assign_action_guidance(row, tier, score):
    has_real_errors = row.get('flag_chronology_error', False) or row.get('flag_salary_error', False) or row.get('flag_trust_error', False)
    notice = row.get('notice_period_days', 0)
    resp = row.get('recruiter_response_rate', 0.0)
    if score < 0.1 or "Tier 5" in tier:
        return "Deprioritize"
    if has_real_errors and score >= 0.4:
        return "Verify Before Interview"
    if "Tier 1" in tier:
        return "Interview Immediately" if resp >= 0.75 else "Priority Screen"
    if "Tier 2" in tier:
        return "Priority Screen"
    if "Tier 3" in tier:
        return "Nurture Candidate" if notice > 60 else "Pipeline Candidate"
    return "Pipeline Candidate"

# ── Recruiter Archetype System (10 archetypes, scored approach) ────

def detect_recruiter_archetype(row):
    yoe = row.get('years_of_experience', 0.0)
    score = row.get('final_score', 0.0)
    is_hg = bool(row.get('is_hidden_gem', False))
    hg_score = row.get('hidden_gem_score', 0.0)
    startup_fit = row.get('score_startup_fit', 0.0)
    behav = row.get('score_behavioral', 0.0)
    resp_rate = row.get('recruiter_response_rate', 0.0)
    open_flag = row.get('open_to_work_flag', False)
    notice = row.get('notice_period_days', 0)
    github = row.get('github_activity_score', -1.0)
    match_skills = row.get('total_jd_skill_matches', 0)
    has_assessments = bool(row.get('skill_assessment_scores', {}))
    interview_rate = row.get('interview_completion_rate', 0.0)

    has_high_risk_flag = (
        row.get('flag_chronology_error', False) or
        row.get('flag_salary_error', False) or
        row.get('flag_honeypot_timeline_inflated', False) or
        row.get('flag_honeypot_skill_inflated', False)
    )
    consulting = row.get('disq_only_consulting', False)
    pure_research = row.get('disq_pure_research', False)
    strong_sigs = github >= 50 or has_assessments or interview_rate >= 0.7

    scores = {}

    if resp_rate >= 0.5 and open_flag:
        rf = resp_rate * 0.40 + behav * 0.30
        if resp_rate >= 0.75:
            rf += 0.30
        scores["Recruiter Favorite"] = min(rf, 1.0)

    if match_skills >= 3 and github >= 30:
        pe = match_skills * 0.08 + min(github / 100, 1.0) * 0.10
        if resp_rate < 0.3:
            pe += 0.40
        elif not open_flag:
            pe += 0.30
        elif resp_rate < 0.5:
            pe += 0.15
        scores["Passive Expert"] = min(pe, 1.0)

    if score >= 0.4 and has_high_risk_flag:
        hr = score * 0.40 + 0.50
        scores["High Risk / High Reward"] = min(hr, 1.0)

    if yoe >= 6 and not pure_research and score >= 0.4:
        pv = min((yoe - 4) / 8, 1.0) * 0.40 + score * 0.40 + min(yoe / 10, 0.20)
        scores["Production Veteran"] = min(pv, 1.0)

    if 2 <= yoe <= 6 and behav >= 0.5:
        gc = (1.0 - abs(yoe - 4.0) / 4.0) * 0.30 + behav * 0.25
        gc += 0.30 if strong_sigs else 0.10
        gc += 0.15 if open_flag else 0.0
        scores["Growth Candidate"] = min(gc, 1.0)

    if yoe < 4.5 and match_skills >= 2:
        es = (1.0 - yoe / 6.0) * 0.30 + match_skills * 0.10 + min(github / 100, 1.0) * 0.15
        es += 0.10 if has_assessments else 0.0
        scores["Emerging Specialist"] = min(es, 1.0)

    if startup_fit >= 0.75 and not consulting and yoe >= 2:
        sb = startup_fit * 0.30 + (0.15 if not pure_research else 0.05) + min(yoe / 20, 0.15)
        scores["Startup Builder"] = min(sb, 1.0)

    if is_hg:
        hg = hg_score / 100.0 * 0.60 + 0.15
        scores["Hidden Gem"] = min(hg, 1.0)

    if score >= 0.4 and not consulting and yoe >= 3:
        pm = score * 0.30 + min(yoe / 12, 1.0) * 0.25 + 0.15
        scores["Product-Minded Engineer"] = min(pm, 1.0)

    if score >= 0.3:
        scores["High Conviction Hire"] = score * 0.30

    if scores:
        return max(scores, key=scores.get)
    return "Consider"


# ── Signal Phrase Banks (hash-varied) ──────────────────────────────
_VDB_PHRASES = [
    "End-to-end retrieval and vector database expertise",
    "Full-stack retrieval systems (vector DBs + dense retrieval)",
    "Production retrieval pipelines and vector search",
    "Vector database and dense retrieval experience",
    "End-to-end search and vector database systems",
]
_EVAL_PHRASES = [
    "Ranking evaluation and learning-to-rank experience",
    "IR evaluation (NDCG/MRR) and ranking optimization",
    "Learning-to-rank and retrieval evaluation expertise",
    "Search quality evaluation and ranking pipelines",
]
_LLM_PHRASES = [
    "LLM fine-tuning experience",
    "Large language model fine-tuning",
    "LLM adaptation and fine-tuning expertise",
]
_DS_PHRASES = [
    "Distributed systems and inference optimization",
    "Scalable ML systems and model serving",
    "Distributed ML pipelines and inference infrastructure",
]
_NLP_PHRASES = [
    "NLP and information retrieval background",
    "Natural language processing and search expertise",
    "Text processing and information retrieval experience",
]
_PY_PHRASES = [
    "Strong Python proficiency",
    "Production Python engineering skills",
    "Python-based ML development expertise",
]

# ── JD alignment phrases (expanded with candidate-specific context injection) ──
_JD_FOUNDING_PHRASES = [
    "Profile signals align with the founding-team, high-autonomy environment described in the JD",
    "Profile signals match the JD's preference for founding-team, high-autonomy settings",
    "Fits the high-autonomy, founding-team context emphasized in the JD",
    "Signals indicate comfort with the JD's described founding-team environment requiring high autonomy",
    "Aligned with the JD's call for a founding-team engineer comfortable with high autonomy",
    "Behavioral profile suggests fit for the high-autonomy, founding-team role described in the JD",
    "The candidate's profile mirrors the JD's founding-team profile where high autonomy is expected",
    "Engagement signals point to a strong fit for the JD's high-autonomy, founding-team environment",
    "This candidate's profile reads like the kind of founder-oriented engineer the JD describes — high autonomy, product-aware, delivery-focused",
    "The JD explicitly emphasizes 'scrappy product-engineering attitude' — this candidate's trajectory demonstrates exactly that balance",
    "Founding-team dynamic described in the JD requires someone who can toggle between deep technical work and pragmatic shipping; this candidate fits that profile",
    "The JD's 'vibe check' section stresses async communication and fast iteration — behavioral signals here are consistent with that environment",
]

_JD_PRODUCTION_PHRASES = [
    "Production experience with retrieval systems aligns with the JD's emphasis on shipped systems over pure research",
    "The JD stresses shipped systems over research — this candidate's production background matches that preference",
    "Practical deployment experience aligns with the JD's stated need for engineering that ships, not just researches",
    "Track record of building production ML systems matches the JD's emphasis on tangible delivery",
    "The candidate's history of deploying retrieval systems into production fits the JD's shipper-over-researcher ideal",
    "Production engineering background resonates with the JD's focus on real-world system delivery",
    "The JD explicitly warns against 'framework enthusiasts' and 'people who have only worked at consulting firms'; this candidate's hands-on product experience addresses that concern directly",
    "This candidate has shipped real ranking or search systems to production — exactly the kind of tangible output the JD prioritizes over 'researcher' archetypes",
    "The JD's core distinction is between researchers who publish and engineers who ship; this candidate clearly lands on the shipper side of that divide",
    "Deploying ML systems to real users at meaningful scale aligns with the first-90-day mandate described in the JD",
]

def _pick_phrase(phrases, cid, offset=0):
    idx = (hash(str(cid)) + offset) % len(phrases) if cid else 0
    return phrases[idx]


def get_positive_signals(row, max_signals=5):
    signals = []
    cid = row.get('candidate_id', '')

    if row.get('match_vector_db', False) and row.get('match_embeddings', False):
        signals.append(_pick_phrase(_VDB_PHRASES, cid, 0))
    elif row.get('match_vector_db', False):
        signals.append(_pick_phrase(_VDB_PHRASES, cid, 2))

    if row.get('match_evaluation', False):
        has_ltr = row.get('match_learning_to_rank', False)
        if has_ltr:
            signals.append(_pick_phrase(_EVAL_PHRASES, cid, 1))
        else:
            signals.append("Ranking evaluation knowledge (NDCG/MRR)")

    if row.get('match_llm_finetune', False):
        signals.append(_pick_phrase(_LLM_PHRASES, cid, 3))

    if row.get('match_distributed_systems', False):
        signals.append(_pick_phrase(_DS_PHRASES, cid, 4))

    if row.get('match_nlp_ir', False):
        signals.append(_pick_phrase(_NLP_PHRASES, cid, 5))

    if row.get('match_python', False):
        signals.append(_pick_phrase(_PY_PHRASES, cid, 6))

    yoe = row.get('years_of_experience', 0.0)
    if yoe >= 8:
        signals.append(f"{yoe:.0f} years of industry experience")
    elif yoe >= 5:
        signals.append(f"{yoe:.0f} years of applied ML experience")

    resp = row.get('recruiter_response_rate', 0.0)
    if resp >= 0.8:
        signals.append(f"Highly responsive to outreach ({resp:.0%})")
    elif resp >= 0.5:
        signals.append(f"Responsive to recruiter messages ({resp:.0%})")

    gh = row.get('github_activity_score', -1.0)
    if gh >= 70:
        signals.append("Active open-source contributor")

    if row.get('score_startup_fit', 0.0) >= 0.8:
        startup_variants = [
            "Startup-friendly profile signals",
            "Career history shows product-company DNA — fits the founding-team ethos",
            "Experience spans early-stage environments which maps to the JD's 'scrappy product-engineering' language",
        ]
        signals.append(startup_variants[(hash(str(cid)) + 3) % len(startup_variants)])

    open_flag = row.get('open_to_work_flag', False)
    if open_flag:
        otw_variants = [
            "Actively open to work",
            "Marked as available — recruiter outreach likely to get a response",
            "Open-to-work flag signals active job search, reducing sourcing friction",
        ]
        signals.append(otw_variants[(hash(str(cid)) + 7) % len(otw_variants)])

    # Inject specific skill names for variety
    raw_skills = row.get('skills_listed', [])
    if raw_skills and len(signals) < max_signals:
        skill_sample = raw_skills[:3]
        skill_variants = [
            f"Hands-on with {', '.join(skill_sample)}",
            f"Technical stack includes {', '.join(skill_sample)}",
        ]
        signals.append(skill_variants[(hash(str(cid)) + 11) % len(skill_variants)])

    return signals[:max_signals]


def get_negative_signals(row):
    concerns = []
    if row.get('flag_chronology_error', False):
        concerns.append("Timeline inconsistencies in career history")
    if row.get('flag_salary_error', False):
        concerns.append("Salary expectation data inconsistency")
    if row.get('flag_trust_error', False):
        concerns.append("No verified contact channels (email/phone/LinkedIn)")
    if row.get('flag_honeypot_timeline_inflated', False):
        concerns.append("Career timeline anomaly detected")
    if row.get('flag_honeypot_skill_inflated', False):
        concerns.append("Expert proficiency with zero duration")
    if row.get('flag_honeypot_title_mismatch', False):
        concerns.append("Keyword count inconsistent with current role")

    if row.get('disq_only_consulting', False):
        concerns.append("Consulting-only background")
    if row.get('disq_pure_research', False):
        concerns.append("Research-heavy profile — limited production deployment")
    if row.get('disq_title_chaser', False):
        concerns.append("Short tenure pattern across roles")
    if row.get('disq_domain_mismatch', False):
        concerns.append("CV/robotics focus rather than NLP/IR/ranking")
    if row.get('disq_inactive_coder', False):
        concerns.append("Potential hands-on coding gap")

    resp = row.get('recruiter_response_rate', 0.0)
    if 0.0 < resp < 0.3:
        concerns.append(f"Low recruiter response rate ({resp:.0%})")
    last_active = row.get('last_active_days_ago', -1)
    if last_active > 90:
        concerns.append(f"Inactive on platform ({last_active} days)")
    notice = row.get('notice_period_days', 0)
    if notice > 60:
        concerns.append(f"Extended notice period ({notice} days)")
    elif notice > 30:
        concerns.append(f"Moderate notice period ({notice} days)")
    salary_min = row.get('expected_salary_min', 0.0)
    if salary_min > 40:
        concerns.append(f"Salary expectation ({salary_min:.0f} LPA min) — verify budget alignment")

    return concerns


def get_additional_concerns(row):
    """Generate additional concerns from subtle signals so every candidate has at least one."""
    extras = []
    if not row.get('open_to_work_flag', False):
        extras.append("Not marked as open to work")
    if row.get('profile_completeness_score', 100) < 60:
        extras.append(f"Profile only {row.get('profile_completeness_score', 0):.0f}% complete")
    if not row.get('match_python', False):
        extras.append("No explicit Python skills listed")
    if not row.get('match_vector_db', False) and not row.get('match_embeddings', False):
        extras.append("No vector DB or embedding experience listed")
    if row.get('github_activity_score', -1) < 30 and row.get('github_activity_score', -1) >= 0:
        extras.append("Limited public code contributions")
    if row.get('applications_submitted_30d', 999) == 0:
        extras.append("No recent job applications on platform")
    if row.get('total_jd_skill_matches', 0) <= 2:
        extras.append(f"Only {row.get('total_jd_skill_matches', 0)} of 9 JD skill categories matched")
    gh = row.get('github_activity_score', -1)
    if gh < 0:
        extras.append("No GitHub profile linked")
    loc = str(row.get('location', '')).lower()
    preferred = ['pune', 'noida', 'bangalore', 'bengaluru', 'mumbai', 'delhi', 'gurgaon', 'gurugram', 'hyderabad', 'chennai']
    if not any(c in loc for c in preferred):
        extras.append(f"Located outside preferred Indian tech hubs ({loc or 'unknown'})")
    if row.get('interview_completion_rate', 1.0) < 0.5:
        extras.append(f"Low interview completion rate ({row.get('interview_completion_rate', 0):.0%})")
    return extras



# ── JD-Aware Assessment ─────────────────────────────────────────────
def get_jd_assessment_markers(row):
    markers = []
    yoe = row.get('years_of_experience', 0.0)

    if yoe >= 5 and not row.get('disq_pure_research', False):
        markers.append("production_depth")
    elif yoe >= 3:
        markers.append("moderate_experience")
    else:
        markers.append("limited_experience")

    if not row.get('disq_pure_research', False) and (row.get('match_vector_db', False) or row.get('match_embeddings', False)):
        markers.append("shipper_profile")
    elif not row.get('disq_pure_research', False):
        markers.append("mixed_production_research")
    else:
        markers.append("research_heavy")

    if row.get('score_startup_fit', 0.0) >= 0.8:
        markers.append("startup_ready")

    if row.get('disq_only_consulting', False):
        markers.append("consulting_concern")
    if row.get('disq_title_chaser', False):
        markers.append("tenure_concern")

    loc = str(row.get('location', '')).lower()
    if any(city in loc for city in ['pune', 'noida', 'delhi', 'gurgaon', 'gurugram', 'mumbai', 'hyderabad', 'bangalore', 'bengaluru', 'chennai']):
        markers.append("india_tech_hub")
    if any(city in loc for city in ['pune', 'noida']):
        markers.append("preferred_location")

    notice = row.get('notice_period_days', 0)
    if notice <= 30:
        markers.append("short_notice")
    elif notice > 60:
        markers.append("long_notice")

    if row.get('match_hr_tech', False):
        markers.append("hr_tech_exposure")

    return markers

# ── NEW: Multiple JD sentence structures ────────────────────────────
_JD_SENTENCE_VARIANTS = [
    # 0: Standard production + founding
    "production_founding",
    # 1: Ship-first framing
    "ship_first",
    # 2: Production only
    "production_only",
    # 3: Founding only
    "founding_only",
    # 4: Tenure/short notice
    "tenure_notice",
    # 5: Location focused
    "location_focused",
    # 6: Research concern
    "research_concern",
    # 7: General alignment
    "general_alignment",
]

def _format_jd_text(markers, row, variant_idx):
    parts = []
    yoe = row.get('years_of_experience', 0.0)
    cid = row.get('candidate_id', '')

    if variant_idx == 0:
        # Production + founding (now varied with candidate details)
        if "production_depth" in markers and "shipper_profile" in markers:
            prod_pick = _pick_phrase(_JD_PRODUCTION_PHRASES, cid, 0)
            # Occasionally append YOE context
            if (hash(str(cid)) + 47) % 5 == 0:
                if "short_notice" in markers:
                    prod_pick += f" — {row.get('notice_period_days', 0)}-day notice supports quick start"
                elif "india_tech_hub" in markers:
                    loc = row.get('location', '')
                    prod_pick += f" — based in {loc}, aligning with regional scope"
            parts.append(prod_pick)
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 7))
        if not parts:
            if "limited_experience" in markers:
                parts.append(f"Experience level ({yoe:.0f} years) is below the JD's preferred 5-9 year range but other signals may compensate")
            else:
                notice = row.get('notice_period_days', 0)
                if notice and notice <= 30:
                    parts.append(f"Quick availability ({notice}-day notice) and experience profile show partial JD alignment")
                else:
                    parts.append("Profile has some alignment with JD requirements")

    elif variant_idx == 1:
        # Ship-first framing
        if "shipper_profile" in markers:
            parts.append("The JD explicitly prioritizes engineers who ship over researchers — this candidate's deployment track record fits that mold")
        elif "research_heavy" in markers:
            parts.append("JD explicitly prioritizes production deployment over research-only paths — candidate's research-heavy background is a noted tension")
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 1))
        if not parts:
            parts.append("Industry experience matches the JD's 5-9 year target range for senior engineers")

    elif variant_idx == 2:
        # Production only
        if "production_depth" in markers:
            if "shipper_profile" in markers:
                parts.append(_pick_phrase(_JD_PRODUCTION_PHRASES, cid, 5))
            else:
                parts.append("Industry experience matches the JD's 5-9 year target range for senior engineers")
        elif "limited_experience" in markers:
            parts.append(f"Experience level ({yoe:.0f} years) is below the JD's preferred 5-9 year range")
        if "short_notice" in markers:
            notice = row.get('notice_period_days', 0)
            parts.append(f"Short notice period ({notice} days) fits the JD's preference for quick availability")
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 2))

    elif variant_idx == 3:
        # Founding focused
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 3))
        if "consulting_concern" in markers:
            parts.append("JD flags consulting-only backgrounds as a potential concern for founding-team roles")
        if "tenure_concern" in markers:
            parts.append("JD seeks founding-team stability — short tenure pattern may be a concern")
        if not parts and "production_depth" in markers:
            parts.append(_pick_phrase(_JD_PRODUCTION_PHRASES, cid, 1))

    elif variant_idx == 4:
        # Tenure/notice focused
        if "long_notice" in markers:
            parts.append(f"{row.get('notice_period_days', 0)}-day notice period exceeds the JD's implied quick-start preference")
        elif "short_notice" in markers:
            parts.append(f"Short notice ({row.get('notice_period_days', 0)} days) aligns with the JD's desire for quick availability")
        if "tenure_concern" in markers:
            parts.append("JD values founding-team stability — candidate's <18-month average tenure is a flagged concern")
        if "production_depth" in markers and "shipper_profile" in markers:
            parts.append(_pick_phrase(_JD_PRODUCTION_PHRASES, cid, 4))
        if not parts and "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 5))

    elif variant_idx == 5:
        # Location focused
        if "preferred_location" in markers:
            parts.append("Located in Pune/Noida — zero relocation friction for the JD's preferred locations")
        elif "india_tech_hub" in markers:
            parts.append("Based in an Indian tech hub — aligns with the JD's geographic scope")
        if "shipper_profile" in markers:
            parts.append(_pick_phrase(_JD_PRODUCTION_PHRASES, cid, 2))
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 6))
        if not parts:
            parts.append("Experience profile broadly aligns with JD requirements")

    elif variant_idx == 6:
        # Research concern focus
        if "research_heavy" in markers:
            parts.append("JD explicitly prioritizes production deployment over research — this candidate has a research-heavy profile that may not align")
        elif "mixed_production_research" in markers:
            parts.append("Candidate has both research and production signals — JD prefers shipper profile but flexibility may apply")
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 4))
        if not parts and "short_notice" in markers:
            parts.append(f"Quick availability ({row.get('notice_period_days', 0)}-day notice) — aligns with JD's speed preference")

    else:
        # General alignment (variant 7) — inject candidate-specific details
        yoe_variants = [
            f"Profile depth ({yoe:.0f} years) aligns with the JD's 5-9 year senior engineer target range",
            f"At {yoe:.0f} years of experience, this candidate falls within the JD's senior engineer range",
        ]
        loc_variants = [
            "Pune/Noida location matches JD preference — no relocation needed",
            "Preferred geography (Pune/Noida) — no relocation cost or timeline risk",
        ]
        hub_variants = [
            "Indian tech hub location fits the JD's geographic scope",
            "Based in a major Indian tech hub — aligns with JD's location preferences",
        ]
        if "production_depth" in markers:
            parts.append(yoe_variants[(hash(str(cid)) + 37) % len(yoe_variants)])
        if "preferred_location" in markers:
            parts.append(loc_variants[(hash(str(cid)) + 41) % len(loc_variants)])
        elif "india_tech_hub" in markers:
            parts.append(hub_variants[(hash(str(cid)) + 43) % len(hub_variants)])
        if "startup_ready" in markers:
            parts.append(_pick_phrase(_JD_FOUNDING_PHRASES, cid, 0))
        if not parts:
            notice = row.get('notice_period_days', 0)
            if notice and notice <= 30:
                parts.append(f"Short notice ({notice} days) reduces hiring timeline risk")
            elif row.get('match_retrieval_ranking') or row.get('match_vector_db'):
                parts.append("Retrieval/ranking experience directly maps to the JD's core technical requirements")
            else:
                parts.append("Candidate's experience has partial alignment with JD requirements — note specific gaps above")

    if not parts:
        parts.append("Profile has some alignment with JD requirements")
    return " \u2014 " + "; ".join(parts)

# ── Recruiter Action Text ──────────────────────────────────────────

def generate_candidate_narratives(df):
    """Generates natural language candidate narratives and recruiter briefings.
    
    Args:
        df (pd.DataFrame): Scored candidates DataFrame.
        
    Returns:
        pd.DataFrame: A copy of the DataFrame with new narrative and tier columns.
    """
    out_df = df.copy()
    
    # Ensure ranked
    if 'rank' not in out_df.columns:
        out_df = out_df.sort_values("final_score", ascending=False).reset_index(drop=True)
        out_df["rank"] = range(1, len(out_df) + 1)
        
    out_df['narrative_tier'] = assign_tiers(out_df)
    
    narratives = []
    archetypes = []
    actions = []
    narrative_strengths_list = []
    narrative_risks_list = []
    narrative_behavioral_list = []
    narrative_recruitability_list = []
    strength_sources_list = []
    risk_sources_list = []
    
    records = out_df.to_dict('records')
    for row in records:
        score = row.get('final_score', 0.0)
        yoe = row.get('years_of_experience', 0.0)
        tier = row.get('narrative_tier', 'Tier 4 - Backup Pool')
        tier_short = tier.split(" - ")[0]
        
        # 1. Archetype Assignment
        arch = detect_archetype(row, score)
        archetypes.append(arch)
        
        # 2. Action Recommendation Assignment
        act = assign_action_guidance(row, tier, score)
        actions.append(act)
        
        # 3. Strength Synthesis (replacing raw keyword dumping with synthesized concepts)
        strengths = []
        strength_src = []
        
        has_rag = row.get('match_vector_db', False) and row.get('match_embeddings', False)
        if has_rag:
            strengths.append("end-to-end retrieval engineering capability across search, ranking, and vector infrastructure")
            strength_src.append("match_vector_db+match_embeddings")
        elif row.get('match_vector_db', False):
            strengths.append("familiarity with vector databases")
            strength_src.append("match_vector_db")
        elif row.get('match_embeddings', False):
            strengths.append("dense retrieval and embeddings concepts")
            strength_src.append("match_embeddings")
            
        if row.get('match_llm_finetune', False):
            strengths.append("hands-on alignment in fine-tuning large language models")
            strength_src.append("match_llm_finetune")
            
        has_ltr = row.get('match_learning_to_rank', False) and row.get('match_evaluation', False)
        if has_ltr:
            strengths.append("strong background in learning-to-rank systems and search relevance evaluation metrics")
            strength_src.append("match_learning_to_rank+match_evaluation")
        elif row.get('match_learning_to_rank', False):
            strengths.append("familiarity with machine learning ranking models")
            strength_src.append("match_learning_to_rank")
        elif row.get('match_evaluation', False):
            strengths.append("knowledge of offline-to-online ranking evaluation")
            strength_src.append("match_evaluation")
            
        if row.get('match_distributed_systems', False):
            strengths.append("ability to build distributed computing systems for high-throughput model inference")
            strength_src.append("match_distributed_systems")
            
        if row.get('match_nlp_ir', False) and not has_rag:
            strengths.append("foundations in natural language processing and search technology")
            strength_src.append("match_nlp_ir")
            
        if row.get('match_python', False) and not (has_rag or has_ltr or row.get('match_llm_finetune', False)):
            strengths.append("Python software engineering foundations")
            strength_src.append("match_python")
            
        if yoe >= 8:
            strengths.append("extensive tenure operating at scale in industry environments")
            strength_src.append("years_of_experience")
        elif yoe >= 4:
            strengths.append("solid experience developing features in engineering settings")
            strength_src.append("years_of_experience")
            
        if row.get('github_activity_score', -1.0) >= 0.7:
            strengths.append("active open-source contribution patterns")
            strength_src.append("github_activity_score")
            
        if row.get('recruiter_response_rate', 0.0) >= 0.85:
            strengths.append("highly prompt communication habits")
            strength_src.append("recruiter_response_rate")
            
        # Format strengths text
        if strengths:
            if len(strengths) == 1:
                strengths_text = strengths[0]
            elif len(strengths) == 2:
                strengths_text = f"{strengths[0]} as well as {strengths[1]}"
            else:
                strengths_text = ", ".join(strengths[:-1]) + f", and {strengths[-1]}"
        else:
            strengths_text = "general profile layout alignment"
            
        narrative_strengths_list.append(strengths_text)
        strength_sources_list.append(", ".join(strength_src) if strength_src else "None")
        
        # 4. Prioritized Risk Handling (focusing on high-priority items, ignoring duplicate name artifacts)
        high_risks = []
        low_risks = []
        risk_src = []
        
        # Chronology, salary, and trust are critical flags
        if row.get('flag_chronology_error', False):
            high_risks.append("critical chronology timeline errors in career dates")
            risk_src.append("flag_chronology_error")
        if row.get('flag_salary_error', False):
            high_risks.append("discrepancies in expected salary numbers")
            risk_src.append("flag_salary_error")
        if row.get('flag_trust_error', False):
            high_risks.append("lack of verified contact channels or profile links")
            risk_src.append("flag_trust_error")
            
        # Medium behavioral risks
        last_active = row.get('last_active_days_ago', -1)
        if last_active > 90:
            high_risks.append("platform inactivity exceeding 3 months")
            risk_src.append("last_active_days_ago")
            
        resp_rate = row.get('recruiter_response_rate', 0.0)
        if resp_rate < 0.3:
            high_risks.append("low response rate to platform outreach")
            risk_src.append("recruiter_response_rate")
            
        # Low disqualification risks
        if row.get('disq_title_chaser', False):
            low_risks.append("a pattern of short tenures and frequent job hops")
            risk_src.append("disq_title_chaser")
        if row.get('disq_inactive_coder', False):
            low_risks.append("potential hands-on coding gap due to management focus")
            risk_src.append("disq_inactive_coder")
        if row.get('disq_only_consulting', False):
            low_risks.append("exclusively consulting firm background")
            risk_src.append("disq_only_consulting")
        if row.get('disq_pure_research', False):
            low_risks.append("pure academic/research path with limited corporate engineering exposure")
            risk_src.append("disq_pure_research")
        if row.get('disq_domain_mismatch', False):
            low_risks.append("focus in computer vision/robotics rather than search and ranking")
            risk_src.append("disq_domain_mismatch")
            
        # Long notice period is a minor risk
        notice = row.get('notice_period_days', 0)
        if notice > 90:
            low_risks.append(f"a lengthy notice period ({notice} days)")
            risk_src.append("notice_period_days")
            
        # We explicitly de-emphasize duplicate identity flags if they appear to be dataset artifacts.
        # We only list it as a minor note if there are no high risks.
        if row.get('flag_duplicate_identity', False) and not (high_risks or low_risks):
            # Dataset artifact warning
            low_risks.append("potential duplicate identity (likely database artifact)")
            risk_src.append("flag_duplicate_identity")
            
        # Synthesize risks text
        all_risks = high_risks + low_risks
        if all_risks:
            if len(all_risks) == 1:
                risks_text = f"Risks to note include {all_risks[0]}."
            elif len(all_risks) == 2:
                risks_text = f"Risks to note include {all_risks[0]} and {all_risks[1]}."
            else:
                risks_text = f"Risks to note include " + ", ".join(all_risks[:-1]) + f", and {all_risks[-1]}."
            risks_summary = ", ".join(all_risks)
        else:
            risks_text = "No significant work history or data quality risks were detected."
            risks_summary = "None detected"
            
        narrative_risks_list.append(risks_summary)
        risk_sources_list.append(", ".join(risk_src) if risk_src else "None")
        
        # 5. Behavioral Interpretation
        avg_time = row.get('avg_response_time_hours', 0.0)
        interview_rate = row.get('interview_completion_rate', 0.0)
        github = row.get('github_activity_score', -1.0)
        
        behavior_clauses = []
        if resp_rate >= 0.85:
            behavior_clauses.append(f"highly responsive (response rate of {resp_rate:.0%})")
        elif resp_rate >= 0.5:
            behavior_clauses.append(f"moderately responsive (response rate of {resp_rate:.0%})")
        else:
            behavior_clauses.append(f"less active or responsive (response rate of {resp_rate:.0%})")
            
        if interview_rate >= 0.8:
            behavior_clauses.append("exhibits excellent interview reliability")
        elif interview_rate > 0.0:
            behavior_clauses.append(f"has an interview completion rate of {interview_rate:.0%}")
            
        if github >= 0.7:
            behavior_clauses.append("demonstrates high coding output on GitHub")
            
        behavioral_text = f"On the platform, they are " + ", ".join(behavior_clauses[:-1]) + f", and {behavior_clauses[-1]}." if len(behavior_clauses) >= 2 else f"On the platform, they are {behavior_clauses[0]}."
        narrative_behavioral_list.append(behavioral_text)
        
        # 6. Recruitability Interpretation (store for narrative_recruitability_list)
        relocate = row.get('willing_to_relocate', False)
        relocate_text = "is open to relocation" if relocate else "prefers local placement"
        sal_min = row.get('expected_salary_min', 0.0)
        sal_max = row.get('expected_salary_max', 0.0)
        
        salary_clause = ""
        if sal_min > 0.0:
            salary_clause = f" with expectations around {sal_min:.0f}-{sal_max:.0f} LPA"
            
        # Simple version for the recruitability column
        recruit_text_simple = f"Notice period is {notice} days, they {relocate_text}{salary_clause}."
        narrative_recruitability_list.append(recruit_text_simple)
        
        # 7. Redesigned Narrative with template variation for diversity
        # Section A: Why this candidate & Archetype context
        thesis_tpl = _select_template(THESIS_TEMPLATES, row.get('candidate_id', ''))
        thesis = thesis_tpl.format(arch=arch, tier_short=tier_short, strengths_text=strengths_text)
        
        # Section B: What makes them different & Behavioral context
        behavior = behavioral_text.replace('On the platform, they are ', '')
        diff_tpl = _select_template(DIFF_TEMPLATES, row.get('candidate_id', ''))
        diff = diff_tpl.format(behavior=behavior)
        
        # Section C: What to verify
        verification_items = []
        if high_risks:
            verification_items.append("verify data discrepancies (" + ", ".join(high_risks) + ")")
        if notice > 60:
            verification_items.append(f"address notice period of {notice} days")
        if sal_min > 40.0:
            verification_items.append(f"confirm budget alignment for {sal_min:.0f} LPA expectations")
            
        if verification_items:
            items_str = " and ".join(verification_items)
            verify_tpl = _select_template(VERIFY_TEMPLATES_WITH_RISKS, row.get('candidate_id', ''))
            verify_clause = verify_tpl.format(items=items_str)
        else:
            verify_tpl = _select_template(VERIFY_TEMPLATES_NO_RISKS, row.get('candidate_id', ''))
            verify_clause = verify_tpl
            
        # Section D: Next Steps / Recruiter Action Guidance
        next_step_tpl = _select_template(NEXT_STEP_TEMPLATES, row.get('candidate_id', ''))
        next_step = next_step_tpl.format(act=act)
        
        # Recruitability text with variation
        recruit_tpl = _select_template(RECRUIT_TEMPLATES, row.get('candidate_id', ''))
        relocate_text = "is open to relocation" if relocate else "prefers local placement"
        relocate_text_subj = "are open to relocation" if relocate else "prefer local placement"
        relocate_text_title = relocate_text.capitalize()
        salary_clause = f" with expectations around {sal_min:.0f}-{sal_max:.0f} LPA" if sal_min > 0.0 else ""
        recruit_text = recruit_tpl.format(notice=notice, relocate_text=relocate_text, relocate_text_subj=relocate_text_subj, relocate_text_title=relocate_text_title, salary_clause=salary_clause)
        
        # Ensure proper spacing - avoid double periods
        comp_narrative = f"{thesis} {diff} {recruit_text} {verify_clause} {next_step}"
        comp_narrative = comp_narrative.replace('.. ', '. ').replace('..', '.')
        narratives.append(comp_narrative)
        
    out_df['archetype'] = archetypes
    out_df['action_recommendation'] = actions
    out_df['narrative_strengths'] = narrative_strengths_list
    out_df['narrative_risks'] = narrative_risks_list
    out_df['narrative_behavioral'] = narrative_behavioral_list
    out_df['narrative_recruitability'] = narrative_recruitability_list
    out_df['strength_sources'] = strength_sources_list
    out_df['risk_sources'] = risk_sources_list
    out_df['narrative'] = narratives
    
    return out_df

