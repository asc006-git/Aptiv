import numpy as np
import pandas as pd


def compute_rap_scores(df):
    """Computes Recruiter Action Prioritization (RAP) Score and related fields.

    RAP answers: "Who should I contact first?"
    
    Four components:
      - Engagement Velocity (35 pts): response rate, response time, interview rate, recency
      - Availability (25 pts): open_to_work, notice period, relocation, work mode
      - Conversion Likelihood (20 pts): offer acceptance, interview rate, GitHub, profile
      - Match Baseline (20 pts): final_score capped

    Args:
        df (pd.DataFrame): DataFrame with parsed, scored, and hidden gem columns.

    Returns:
        pd.Series: RAP Score (0-100)
    """
    # --- Engagement Velocity (35 points) ---
    resp_rate = df.get('recruiter_response_rate', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    avg_resp_hrs = df.get('avg_response_time_hours', pd.Series(999, index=df.index)).fillna(999).astype(float)
    interview_rate = df.get('interview_completion_rate', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    last_active = df.get('last_active_days_ago', pd.Series(999, index=df.index)).fillna(999).astype(float)

    resp_speed = np.clip(1.0 - (avg_resp_hrs / 72.0), 0.0, 1.0)
    recency = np.clip(1.0 - (last_active / 90.0), 0.0, 1.0)

    ev = (
        0.40 * resp_rate +
        0.25 * resp_speed +
        0.20 * interview_rate +
        0.15 * recency
    )
    engagement_velocity = ev * 35.0

    # --- Availability (25 points) ---
    open_flag = df.get('open_to_work_flag', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    notice = df.get('notice_period_days', pd.Series(180, index=df.index)).fillna(180).astype(float)
    relocate = df.get('willing_to_relocate', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    work_mode = df.get('preferred_work_mode', pd.Series('', index=df.index)).fillna('')

    notice_score = np.clip(1.0 - (notice / 120.0), 0.0, 1.0)
    mode_flex = work_mode.isin(['remote', 'flexible']).astype(float) * 0.5 + 0.5

    availability = (
        0.40 * open_flag.astype(float) +
        0.35 * notice_score +
        0.15 * relocate.astype(float) +
        0.10 * mode_flex
    )
    availability_component = availability * 25.0

    # --- Conversion Likelihood (20 points) ---
    oar = df.get('offer_acceptance_rate', pd.Series(-1.0, index=df.index)).fillna(-1.0).astype(float)
    oar_norm = np.where(oar >= 0, oar, 0.5)  # -1 (unknown) → 0.5

    github = df.get('github_activity_score', pd.Series(-1.0, index=df.index)).fillna(-1.0).astype(float)
    github_active = (github >= 50).astype(float) * 0.7 + 0.3  # 1.0 if active, 0.3 if not

    profile_complete = df.get('profile_completeness_score', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)

    conv = (
        0.35 * oar_norm +
        0.25 * interview_rate +
        0.20 * github_active +
        0.20 * (profile_complete / 100.0)
    )
    conversion_likelihood = conv * 20.0

    # --- Match Baseline (20 points) ---
    final_score = df.get('final_score', pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    match_baseline = np.clip(final_score * 20.0, 0.0, 20.0)

    # --- Composite RAP Score ---
    rap_score = engagement_velocity + availability_component + conversion_likelihood + match_baseline
    rap_score = np.clip(rap_score, 0.0, 100.0)

    return rap_score


def assign_rap_priority(rap_score):
    """Assigns recruiter action priority category based on RAP Score.

    Args:
        rap_score (pd.Series): RAP Score (0-100).

    Returns:
        pd.Series: Priority category labels.
    """
    conditions = [
        rap_score >= 80,
        rap_score >= 65,
        rap_score >= 45,
        rap_score >= 25,
    ]
    choices = [
        "Contact Immediately",
        "Priority Outreach",
        "Standard Outreach",
        "Long-Term Nurture",
    ]
    return pd.Series(np.select(conditions, choices, default="Do Not Prioritize"), index=rap_score.index)


def generate_rap_action(row, priority):
    """Generates a one-line recruiter action instruction.

    Args:
        row (pd.Series): A single candidate row.
        priority (str): RAP priority category.

    Returns:
        str: Action instruction.
    """
    resp_rate = row.get('recruiter_response_rate', 0)
    open_flag = row.get('open_to_work_flag', False)
    notice = row.get('notice_period_days', 0)
    relocate = row.get('willing_to_relocate', False)

    parts = []
    if resp_rate >= 0.7:
        parts.append(f"{resp_rate:.0%} response rate")
    if open_flag:
        parts.append("open to work")
    if notice <= 30:
        parts.append(f"{notice}-day notice")
    elif notice > 60:
        parts.append(f"{notice}-day notice (plan ahead)")
    if relocate:
        parts.append("willing to relocate")

    detail = ", ".join(parts) if parts else None

    action_map = {
        "Contact Immediately": f"Message NOW. Candidate is highly responsive and available.",
        "Priority Outreach": f"Send message within 24 hours.",
        "Standard Outreach": f"Add to outreach queue this week.",
        "Long-Term Nurture": f"Add to nurture sequence. Reassess in 30-60 days.",
        "Do Not Prioritize": f"Not recommended for current outreach investment.",
    }

    action = action_map.get(priority, "Standard Outreach")
    if detail:
        action += f" Signals: {detail}."
    return action


def generate_rap_rationale(row, priority):
    """Generates a one-sentence explanation of the RAP decision.

    Args:
        row (pd.Series): A single candidate row.
        priority (str): RAP priority category.

    Returns:
        str: Rationale sentence.
    """
    resp_rate = row.get('recruiter_response_rate', 0)
    open_flag = row.get('open_to_work_flag', False)
    notice = row.get('notice_period_days', 0)
    score = row.get('final_score', 0)

    if priority == "Contact Immediately":
        if open_flag:
            return f"Top outreach priority: {resp_rate:.0%} response rate + actively seeking + {notice}-day notice."
        else:
            return f"Top outreach priority: {resp_rate:.0%} response rate indicates high engagement."
    elif priority == "Priority Outreach":
        return f"Strong engagement ({resp_rate:.0%} response) with reasonable availability ({notice}-day notice)."
    elif priority == "Standard Outreach":
        return f"Moderate signals. Standard outreach cadence recommended."
    elif priority == "Long-Term Nurture":
        return f"Good match (score {score:.2f}) but availability limited. Nurture until notice period shortens."
    else:
        return f"Low engagement or availability. Reassess when platform activity renews."


def compute_rap(df):
    """Full RAP computation pipeline.

    Args:
        df (pd.DataFrame): DataFrame with parsed, scored, and hidden gem columns.

    Returns:
        pd.DataFrame: Copy of df with new columns:
            - rap_score (float)
            - rap_priority (str)
            - rap_action (str)
            - rap_rationale (str)
    """
    out_df = df.copy()

    rap_score = compute_rap_scores(out_df)
    out_df['rap_score'] = rap_score.round(2)

    out_df['rap_priority'] = assign_rap_priority(rap_score)

    actions = []
    rationales = []
    for i in range(len(out_df)):
        actions.append(generate_rap_action(out_df.iloc[i], out_df['rap_priority'].iloc[i]))
        rationales.append(generate_rap_rationale(out_df.iloc[i], out_df['rap_priority'].iloc[i]))

    out_df['rap_action'] = actions
    out_df['rap_rationale'] = rationales

    return out_df
