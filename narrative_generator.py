import pandas as pd
import numpy as np

# Template variations for narrative diversity
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
    """Assigns narrative tiers to candidates based on their final score rank
    and data quality flags.
    
    Tiers are defined as:
    - Tier 1: Interview Immediately (Top 2% of candidates)
    - Tier 2: Strong Pipeline (Top 2% to 10% of candidates)
    - Tier 3: Worth a Screen (Top 10% to 25% of candidates)
    - Tier 4: Backup Pool (Top 25% to 75% of candidates)
    - Tier 5: Not Recommended (Bottom 25% of candidates, or score < 0.1)
    
    Args:
        df (pd.DataFrame): Scored candidates DataFrame, sorted by final_score descending.
        
    Returns:
        pd.Series: Series of tier labels.
    """
    total_candidates = len(df)
    if total_candidates == 0:
        return pd.Series(dtype=str)
        
    tiers = np.empty(total_candidates, dtype=object)
    ranks = np.arange(1, total_candidates + 1)
    
    p2 = int(0.02 * total_candidates)
    p10 = int(0.10 * total_candidates)
    p25 = int(0.25 * total_candidates)
    p75 = int(0.75 * total_candidates)
    
    for i in range(total_candidates):
        score = df.iloc[i].get('final_score', 0.0)
        
        # Extremely low score goes directly to Tier 5
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
    """Determines actionable next steps for a recruiter based on tier, score, and risks."""
    has_real_errors = row.get('flag_chronology_error', False) or row.get('flag_salary_error', False) or row.get('flag_trust_error', False)
    notice = row.get('notice_period_days', 0)
    resp = row.get('recruiter_response_rate', 0.0)
    
    if score < 0.1 or "Tier 5" in tier:
        return "Deprioritize"
        
    if has_real_errors and score >= 0.4:
        return "Verify Before Interview"
        
    if "Tier 1" in tier:
        if resp >= 0.75:
            return "Interview Immediately"
        return "Priority Screen"
        
    if "Tier 2" in tier:
        return "Priority Screen"
        
    if "Tier 3" in tier:
        if notice > 60:
            return "Nurture Candidate"
        return "Pipeline Candidate"
        
    if "Tier 4" in tier:
        return "Pipeline Candidate"
        
    return "Pipeline Candidate"

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
