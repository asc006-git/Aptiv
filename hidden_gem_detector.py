import numpy as np
import pandas as pd


def _has_strong_assessments(assessment_dict):
    """Check if skill_assessment_scores has at least 2 scores >= 70."""
    if not isinstance(assessment_dict, dict):
        return False
    count = sum(1 for v in assessment_dict.values() if isinstance(v, (int, float)) and v >= 70)
    return count >= 2


def _norm_github(score):
    """Normalize github_activity_score (-1..100) to 0..1."""
    if score < 0:
        return 0.0
    return min(float(score) / 100.0, 1.0)


def _norm_market_demand(views, saves):
    """Log-scale normalize market demand signals (vectorized)."""
    import numpy as np
    total = np.asarray(views, dtype=float) + np.asarray(saves, dtype=float) * 3.0
    total = np.maximum(total, 0.0)
    result = np.where(total > 0, np.log1p(total) / np.log1p(100), 0.0)
    return np.clip(result, 0.0, 1.0)


def compute_hidden_gem_score(df):
    """Computes Hidden Gem Score (0-100) for each candidate.

    The score measures potential that keyword-based ranking would miss,
    combining behavioral excellence, skill adjacency, technical evidence,
    growth trajectory, market demand, and recruitability.

    Args:
        df (pd.DataFrame): DataFrame with parsed + scored columns.

    Returns:
        pd.Series: Hidden Gem Score (0-100).
    """
    # Behavioral Excellence (30%)
    score_behav = df.get('score_behavioral', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    comp_behav = score_behav * 30.0

    # Skill Adjacency (20%) — peaks when skill_match ~0.4
    score_skill = df.get('score_skill_match', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    adjacency = np.clip(1.0 - np.abs(score_skill - 0.4) / 0.3, 0.0, 1.0)
    comp_adjacency = adjacency * 20.0

    # Technical Evidence (20%) — github + skill assessments
    github = df.get('github_activity_score', pd.Series(-1.0, index=df.index)).fillna(-1.0)
    github_norm = github.apply(_norm_github)
    assessments = df.get('skill_assessment_scores', pd.Series({}))
    has_assess = assessments.apply(_has_strong_assessments).astype(float)
    comp_technical = (github_norm + has_assess * 0.5) * 20.0

    # Growth Trajectory (15%) — startup fit
    startup_fit = df.get('score_startup_fit', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    comp_growth = startup_fit * 15.0

    # Market Demand (10%) — views + saves
    views = df.get('profile_views_received_30d', pd.Series(0, index=df.index)).fillna(0).astype(float)
    saves = df.get('saved_by_recruiters_30d', pd.Series(0, index=df.index)).fillna(0).astype(float)
    demand_norm = _norm_market_demand(views, saves)
    comp_demand = demand_norm * 10.0

    # Recruitability (5%) — open to work + willing to relocate
    open_flag = df.get('open_to_work_flag', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    relocate_flag = df.get('willing_to_relocate', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    recruitability = (open_flag.astype(float) * 3.0 + relocate_flag.astype(float) * 2.0) / 5.0
    comp_recruit = recruitability * 5.0

    # Composite score
    hg_score = comp_behav + comp_adjacency + comp_technical + comp_growth + comp_demand + comp_recruit
    hg_score = np.clip(hg_score, 0.0, 100.0)

    return hg_score


def assign_hidden_gem_category(df, hg_score):
    """Assigns a Hidden Gem category to each candidate.

    Categories are mutually exclusive (first match wins):

    - Emerging Specialist: Skill assessments + low keyword matches
    - Growth Candidate: 2-5yr exp + high behavioral + high startup fit
    - High Intent Candidate: Open + high response + high interview + recent
    - Underexposed Expert: High skill match + low visibility + high GitHub
    - Startup Builder: High startup fit + distributed systems + GitHub + relocate

    Args:
        df (pd.DataFrame): Candidate DataFrame with parsed/scored columns.
        hg_score (pd.Series): Hidden Gem Score.

    Returns:
        pd.Series: Category label strings. None if not a Hidden Gem.
    """
    is_hg = hg_score >= 60.0
    categories = []

    for i in range(len(df)):
        if not is_hg.iloc[i]:
            categories.append(None)
            continue

        row = df.iloc[i]

        # 1. Emerging Specialist
        assessments = row.get('skill_assessment_scores', {})
        total_skill_matches = row.get('total_jd_skill_matches', 0)
        if _has_strong_assessments(assessments) and total_skill_matches <= 4:
            categories.append("Emerging Specialist")
            continue

        # 2. Growth Candidate
        yoe = row.get('years_of_experience', 0)
        behav = row.get('score_behavioral', 0)
        startup = row.get('score_startup_fit', 0)
        if 2 <= yoe <= 5 and behav >= 0.75 and startup >= 0.7:
            categories.append("Growth Candidate")
            continue

        # 3. High Intent Candidate
        open_flag = row.get('open_to_work_flag', False)
        resp_rate = row.get('recruiter_response_rate', 0)
        interview_rate = row.get('interview_completion_rate', 0)
        last_active = row.get('last_active_days_ago', 999)
        if open_flag and resp_rate >= 0.8 and interview_rate >= 0.8 and last_active <= 30:
            categories.append("High Intent Candidate")
            continue

        # 4. Underexposed Expert
        skill_match = row.get('score_skill_match', 0)
        views = row.get('profile_views_received_30d', 0)
        saves = row.get('saved_by_recruiters_30d', 0)
        github = row.get('github_activity_score', -1)
        if skill_match >= 0.5 and (views + saves) < 10 and github >= 50:
            categories.append("Underexposed Expert")
            continue

        # 5. Startup Builder
        match_dist = row.get('match_distributed_systems', False)
        relocate = row.get('willing_to_relocate', False)
        if startup >= 0.8 and match_dist and github >= 50 and relocate:
            categories.append("Startup Builder")
            continue

        categories.append("Hidden Gem")

    return pd.Series(categories, index=df.index)


def generate_hidden_gem_narrative(row, category):
    """Generates a 2-3 sentence recruiter briefing for a Hidden Gem candidate.

    Args:
        row (pd.Series): A single candidate row.
        category (str): The assigned Hidden Gem category.

    Returns:
        str: Narrative text, or empty string if not a Hidden Gem.
    """
    if not category:
        return ""

    templates = {
        "Emerging Specialist": (
            "Validated expertise in specific JD-relevant skills through platform assessments, "
            "yet overall keyword match is modest. This suggests focused depth rather than broad resume optimization — "
            "often signals genuine hands-on capability. Worth a conversation to verify depth."
        ),
        "Growth Candidate": (
            "Early-to-mid-career with strong behavioral signals and startup-fit indicators. "
            "High engagement and growth trajectory suggest potential to ramp quickly. "
            "May lack some keywords but demonstrates learning velocity and reliability."
        ),
        "High Intent Candidate": (
            "Actively on the market, highly responsive, and reliable in interview attendance. "
            "Low friction candidate — ready to engage immediately. "
            "Ideal for roles requiring quick hiring velocity."
        ),
        "Underexposed Expert": (
            "Strong skill match with JD but low platform visibility — undersourced by traditional search. "
            "Active GitHub contributions provide independent technical evidence. "
            "Likely missed by keyword-only ranking; represents a sourcing edge."
        ),
        "Startup Builder": (
            "Combines distributed systems experience with startup-friendly profile — "
            "willing to relocate, builds end-to-end, and ships production code. "
            "Fits high-autonomy, ambiguous environments well."
        ),
    }

    base = templates.get(category, "Displays strong potential signals that traditional keyword ranking may undervalue.")

    yoe = row.get('years_of_experience', 0)
    behav = row.get('score_behavioral', 0)
    response_rate = row.get('recruiter_response_rate', 0)

    context = f" {yoe:.0f}yr experience, behavioral score {behav:.2f}, recruiter response rate {response_rate:.0%}."

    return base + context


def detect_hidden_gems(df):
    """Full Hidden Gem detection pipeline.

    Computes Hidden Gem Score, assigns categories, generates narratives,
    and adds all output columns to the DataFrame.

    Args:
        df (pd.DataFrame): Scored candidate DataFrame.

    Returns:
        pd.DataFrame: Copy of df with new columns:
            - hidden_gem_score (float)
            - is_hidden_gem (bool)
            - hidden_gem_category (str or None)
            - hidden_gem_narrative (str)
    """
    out_df = df.copy()

    hg_score = compute_hidden_gem_score(out_df)
    out_df['hidden_gem_score'] = hg_score.round(2)
    out_df['is_hidden_gem'] = hg_score >= 60.0

    categories = assign_hidden_gem_category(out_df, hg_score)
    out_df['hidden_gem_category'] = categories

    narratives = []
    for i in range(len(out_df)):
        narratives.append(generate_hidden_gem_narrative(out_df.iloc[i], categories.iloc[i]))
    out_df['hidden_gem_narrative'] = narratives

    return out_df
