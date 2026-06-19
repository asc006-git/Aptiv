import json
import re
import pandas as pd
import numpy as np
from datetime import datetime

# Pre-compiled regex patterns
_ACRONYM_PATTERNS = {acro: re.compile(r'\b' + re.escape(acro) + r'\b') for acro in ('ndcg', 'mrr', 'map', 'ltr', 'nlp', 'ir')}
_CONSULTING_CLEAN_RE = re.compile(r'\b(limited|ltd|solutions|services|pvt|corp|corporation|inc)\b')

# Curated JD Skill Keywords
SKILL_KEYWORDS = {
    'vector_db': [
        'pinecone', 'weaviate', 'qdrant', 'milvus', 'opensearch', 'elasticsearch', 
        'faiss', 'hybrid search', 'vector db', 'vector database', 'dense retrieval'
    ],
    'embeddings': [
        'sentence-transformers', 'sentence transformer', 'embeddings', 'bge', 'e5', 
        'dense retrieval', 'embedding drift', 'index refresh'
    ],
    'evaluation': [
        'ndcg', 'mrr', 'map', 'offline-to-online', 'a/b test', 'ab test', 
        'ranking evaluation', 'evaluation framework'
    ],
    'python': [
        'python'
    ],
    'llm_finetune': [
        'lora', 'qlora', 'peft', 'fine-tune', 'fine-tuning', 'finetuning', 'finetune'
    ],
    'learning_to_rank': [
        'xgboost', 'lightgbm', 'learning-to-rank', 'learning to rank', 'ltr'
    ],
    'nlp_ir': [
        'nlp', 'information retrieval', 'natural language processing', 'search', 
        'ranking', 'recommendation', 'retrieval'
    ],
    'distributed_systems': [
        'distributed systems', 'ray', 'spark', 'triton', 'onnx', 'tensorrt', 
        'kubernetes', 'inference optimization', 'large-scale inference'
    ],
    'hr_tech': [
        'hr-tech', 'hr tech', 'recruiting tech', 'marketplace', 'talent intelligence'
    ]
}

# Acronyms where word boundaries are critical to avoid false positives
ACRONYMS = {'ndcg', 'mrr', 'map', 'ltr', 'nlp', 'ir'}

# Heuristic lists for Disqualifier checks
CONSULTING_COMPANIES = {
    'tcs', 'tata consultancy services', 'infosys', 'wipro', 'accenture', 'cognizant', 
    'capgemini', 'hcl', 'hcltech', 'hcl technologies', 'tech mahindra', 'l&t', 'lnt', 
    'mindtree', 'mphasis', 'wipro limited', 'cognizant technology solutions'
}

RESEARCH_WORDS = {'research', 'phd', 'postdoc', 'fellow', 'academic', 'student', 'intern', 'graduate assistant', 'teaching assistant', 'university', 'professor', 'lecturer'}
ENGINEERING_WORDS = {'engineer', 'developer', 'architect', 'lead', 'programmer', 'manager', 'director', 'specialist', 'analyst', 'consultant', 'scientist'}

CV_SPEECH_ROBOTICS_KEYWORDS = {
    'computer vision', 'speech', 'robotics', 'image classification', 'object detection', 
    'speech recognition', 'tts', 'asr', 'cnn', 'yolo', 'opencv', 'audio processing', 'text-to-speech'
}
NLP_IR_KEYWORDS = {
    'nlp', 'ir', 'natural language processing', 'information retrieval', 'llm', 'embeddings', 
    'vector database', 'hybrid search', 'rag', 'ranking', 'search', 'retrieval', 'recommendation'
}

def search_keywords(text_lower, keywords):
    """Helper function to look up pre-defined keywords with boundary checks for acronyms."""
    for kw in keywords:
        if kw in ACRONYMS:
            if _ACRONYM_PATTERNS[kw].search(text_lower):
                return True
        else:
            if kw in text_lower:
                return True
    return False

class CandidateParser:
    def __init__(self):
        # We track anonymized names dynamically to flag potential duplicate identities
        self.seen_names = {}
        # Reference date used for calculating active days ago. Will be set dynamically or default to current date.
        self.max_active_date = None

    def extract_flat_features(self, cand):
        """Extracts flat features from a single candidate dictionary representation."""
        cid = cand.get('candidate_id')
        profile = cand.get('profile', {})
        signals = cand.get('redrob_signals', {})
        history = cand.get('career_history', [])
        skills = cand.get('skills', [])
        education = cand.get('education', [])
        
        name = profile.get('anonymized_name', '')
        
        # Track duplicate names
        if name:
            self.seen_names[name] = self.seen_names.get(name, 0) + 1

        # Concatenate text sources for rich keyword matching
        headline = profile.get('headline', '')
        summary = profile.get('summary', '')
        history_desc = " ".join(job.get('description', '') for job in history)
        skills_str = " ".join(s.get('name', '') for s in skills)
        
        full_text = f"{headline} {summary} {history_desc}".lower()
        skills_lower = skills_str.lower()
        
        # Match JD Skills
        features = {}
        total_matches = 0
        for category, kws in SKILL_KEYWORDS.items():
            has_match = search_keywords(skills_lower, kws) or search_keywords(full_text, kws)
            features[f'match_{category}'] = has_match
            if has_match:
                total_matches += 1
        features['total_jd_skill_matches'] = total_matches
        features['skills_listed'] = " ".join(s.get('name', '') for s in skills)[:200]
        
        # Disqualifiers
        # 1. Consulting only
        features['disq_only_consulting'] = self._check_only_consulting(history)
        
        # 2. Pure research
        features['disq_pure_research'] = self._check_pure_research(history)
        
        # 3. Inactive coder
        features['disq_inactive_coder'] = self._check_inactive_coder(history)
        
        # 4. Title chaser
        features['disq_title_chaser'] = self._check_title_chaser(history)
        
        # 5. Domain Mismatch
        features['disq_domain_mismatch'] = self._check_domain_mismatch(skills_lower, full_text)

        # Behavioral signals
        features['profile_completeness_score'] = signals.get('profile_completeness_score', 0.0)
        features['recruiter_response_rate'] = signals.get('recruiter_response_rate', 0.0)
        features['avg_response_time_hours'] = signals.get('avg_response_time_hours', 0.0)
        features['github_activity_score'] = signals.get('github_activity_score', -1.0)
        features['interview_completion_rate'] = signals.get('interview_completion_rate', 0.0)
        features['offer_acceptance_rate'] = signals.get('offer_acceptance_rate', -1.0)
        features['notice_period_days'] = signals.get('notice_period_days', 0)
        features['willing_to_relocate'] = signals.get('willing_to_relocate', False)
        features['open_to_work_flag'] = signals.get('open_to_work_flag', False)

        # Hidden Gem signals
        features['profile_views_received_30d'] = signals.get('profile_views_received_30d', 0)
        features['saved_by_recruiters_30d'] = signals.get('saved_by_recruiters_30d', 0)
        features['search_appearance_30d'] = signals.get('search_appearance_30d', 0)
        features['connection_count'] = signals.get('connection_count', 0)
        features['endorsements_received'] = signals.get('endorsements_received', 0)
        features['skill_assessment_scores'] = signals.get('skill_assessment_scores', {})
        features['preferred_work_mode'] = signals.get('preferred_work_mode', '')
        features['applications_submitted_30d'] = signals.get('applications_submitted_30d', 0)
        
        sal = signals.get('expected_salary_range_inr_lpa', {})
        features['expected_salary_min'] = sal.get('min', 0.0)
        features['expected_salary_max'] = sal.get('max', 0.0)
        
        # Verifications
        is_email = signals.get('verified_email', False)
        is_phone = signals.get('verified_phone', False)
        is_linkedin = signals.get('linkedin_connected', False)
        
        # Data Quality Flags
        # 1. Chronology error
        signup_str = signals.get('signup_date', '')
        active_str = signals.get('last_active_date', '')
        chronology_err = False
        if signup_str and active_str:
            try:
                signup_dt = datetime.strptime(signup_str, "%Y-%m-%d")
                active_dt = datetime.strptime(active_str, "%Y-%m-%d")
                if active_dt < signup_dt:
                    chronology_err = True
            except ValueError:
                pass
        features['flag_chronology_error'] = chronology_err
        
        # 2. Salary error
        features['flag_salary_error'] = features['expected_salary_max'] < features['expected_salary_min']
        
        # 3. Trust error
        features['flag_trust_error'] = not is_email and not is_phone and not is_linkedin

        # Honeypot H1: timeline inflated
        total_career_months = sum(job.get('duration_months', 0) or 0 for job in history)
        exp_years = profile.get('years_of_experience', 0.0)
        exp_months = exp_years * 12.0
        any_job_over_total = False
        if exp_months > 0:
            for job in history:
                job_dur = job.get('duration_months', 0) or 0
                if job_dur > exp_months:
                    any_job_over_total = True
                    break
        features['flag_honeypot_timeline_inflated'] = (
            any_job_over_total or 
            (exp_months > 0 and total_career_months > exp_months * 1.5)
        )

        # Honeypot H2: skill inflated
        has_inflated_skill = False
        for s in skills:
            prof = s.get('proficiency', '')
            dur = s.get('duration_months', -1)
            if prof in ('advanced', 'expert') and dur == 0:
                has_inflated_skill = True
                break
        features['flag_honeypot_skill_inflated'] = has_inflated_skill

        # Honeypot H3: title mismatch
        title_lower = profile.get('current_title', '').lower()
        ENG_TITLE_WORDS = {'engineer', 'developer', 'scientist', 'architect',
                           'researcher', 'data engineer', 'data scientist',
                           'ml', 'machine learning', 'ai',
                           'software', 'programmer', 'technologist',
                           'full stack', 'fullstack', 'backend', 'frontend', 'devops',
                           'infrastructure', 'platform'}
        is_eng_title = any(w in title_lower for w in ENG_TITLE_WORDS)
        features['flag_honeypot_title_mismatch'] = (total_matches >= 4 and not is_eng_title)

        # Basic Info
        features['candidate_id'] = cid
        features['anonymized_name'] = name
        features['current_title'] = profile.get('current_title', '')
        features['current_company'] = profile.get('current_company', '')
        features['years_of_experience'] = profile.get('years_of_experience', 0.0)
        features['location'] = profile.get('location', '')
        features['country'] = profile.get('country', '')
        
        # Keep track of active date to compute relative recency later
        features['raw_last_active_date'] = active_str
        
        return features

    def _check_only_consulting(self, history):
        if not history:
            return False
        consulting_set = CONSULTING_COMPANIES
        clean_re = _CONSULTING_CLEAN_RE
        for job in history:
            company_lower = job.get('company', '').strip().lower()
            cleaned_company = clean_re.sub('', company_lower).strip()
            is_consulting = False
            for c in consulting_set:
                if c in company_lower or company_lower in c or c in cleaned_company:
                    is_consulting = True
                    break
            if not is_consulting:
                return False
        return True

    def _check_pure_research(self, history):
        if not history:
            return False
        
        all_research = True
        for job in history:
            title_lower = job.get('title', '').strip().lower()
            company_lower = job.get('company', '').strip().lower()
            
            is_research = False
            if any(w in title_lower for w in RESEARCH_WORDS) or 'university' in company_lower or 'institute' in company_lower:
                if any(w in title_lower for w in ENGINEERING_WORDS) and not any(w in title_lower for w in ['student', 'intern', 'assistant']):
                    is_research = False
                else:
                    is_research = True
            if not is_research:
                all_research = False
                break
        return all_research

    def _check_inactive_coder(self, history):
        current_jobs = [job for job in history if job.get('is_current')]
        if not current_jobs and history:
            current_jobs = [history[0]]
            
        for job in current_jobs:
            title_lower = job.get('title', '').lower()
            duration = job.get('duration_months', 0)
            
            is_management = any(w in title_lower for w in ['manager', 'director', 'head', 'architect', 'tech lead', 'technical lead'])
            has_hands_on = any(w in title_lower for w in ['software', 'developer', 'engineer', 'ml', 'ai', 'programmer', 'coder'])
            
            if is_management and not has_hands_on and duration > 18:
                return True
        return False

    def _check_title_chaser(self, history):
        if len(history) < 3:
            return False
        total_months = sum(job.get('duration_months', 0) for job in history)
        avg_duration = total_months / len(history)
        return avg_duration < 18.0

    def _check_domain_mismatch(self, skills_lower, text_lower):
        has_cv_speech = False
        for kw in CV_SPEECH_ROBOTICS_KEYWORDS:
            if kw in skills_lower or kw in text_lower:
                has_cv_speech = True
                break
        if not has_cv_speech:
            return False
            
        has_nlp_ir = False
        for kw in NLP_IR_KEYWORDS:
            if kw in skills_lower or kw in text_lower:
                has_nlp_ir = True
                break
        return not has_nlp_ir

def parse_jsonl(file_path):
    """Streams a candidate JSONL file line by line and parses candidate features.
    
    Args:
        file_path (str): Absolute or relative path to the candidate JSONL file.
        
    Returns:
        pd.DataFrame: A memory-efficient Pandas DataFrame containing flat parsed features.
    """
    parser = CandidateParser()
    parsed_candidates = []
    
    # 1. First pass extraction
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            cand_dict = json.loads(line_str)
            flat_features = parser.extract_flat_features(cand_dict)
            parsed_candidates.append(flat_features)
            
    if not parsed_candidates:
        return pd.DataFrame()
        
    # 2. Post-processing
    # Collect all active dates to compute recency relative to maximum dataset activity
    valid_dates = []
    for c in parsed_candidates:
        date_str = c.get('raw_last_active_date', '')
        if date_str:
            try:
                valid_dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
            except ValueError:
                pass
                
    max_active_dt = max(valid_dates) if valid_dates else datetime.now()
    
    # Apply post-processing flags: relative recency and duplicate name flags
    for c in parsed_candidates:
        # Calculate active days ago
        date_str = c.pop('raw_last_active_date', '')
        days_ago = -1
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                days_ago = (max_active_dt - dt).days
            except ValueError:
                pass
        c['last_active_days_ago'] = days_ago
        
        # Check duplicate identity
        name = c.get('anonymized_name', '')
        is_duplicate = False
        if name and parser.seen_names.get(name, 0) > 1:
            is_duplicate = True
        c['flag_duplicate_identity'] = is_duplicate
        
        # Final Suspicious Profile categorization
        c['is_suspicious_profile'] = (
            c['flag_chronology_error'] or 
            c['flag_salary_error'] or 
            c['flag_trust_error'] or 
            c['flag_duplicate_identity'] or
            c['flag_honeypot_timeline_inflated'] or
            c['flag_honeypot_skill_inflated'] or
            c['flag_honeypot_title_mismatch']
        )
        
    # 3. Create Pandas DataFrame
    df = pd.DataFrame(parsed_candidates)
    
    # Optimize data types to minimize memory footprint
    bool_cols = [col for col in df.columns if col.startswith('match_') or col.startswith('disq_') or col.startswith('flag_') or col == 'is_suspicious_profile']
    for col in bool_cols:
        df[col] = df[col].astype(bool)
        
    int_cols = ['total_jd_skill_matches', 'last_active_days_ago', 'notice_period_days']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype(np.int32)
            
    float_cols = ['profile_completeness_score', 'recruiter_response_rate', 'avg_response_time_hours', 
                  'github_activity_score', 'interview_completion_rate', 'offer_acceptance_rate', 
                  'expected_salary_min', 'expected_salary_max', 'years_of_experience',
                  'profile_views_received_30d', 'saved_by_recruiters_30d', 'search_appearance_30d',
                  'connection_count', 'endorsements_received', 'applications_submitted_30d']
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].astype(np.float32)
            
    return df
