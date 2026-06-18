import pandas as pd
import numpy as np

class CandidateScorer:
    def __init__(self, weights=None):
        """Initializes the scorer with adjustable weights.
        
        Args:
            weights (dict, optional): Custom weights dictionary. Defaults to the JD specifications:
                - SkillMatch: 0.40
                - ProductionExperience: 0.25
                - RetrievalRankingExperience: 0.15
                - BehavioralScore: 0.10
                - StartupFit: 0.10
        """
        self.weights = weights or {
            'skill_match': 0.40,
            'production_experience': 0.25,
            'retrieval_ranking': 0.15,
            'behavioral': 0.10,
            'startup_fit': 0.10
        }
        
    def compute_skill_match_score(self, df):
        """Computes the Skill Match Score.
        Mandatory skills are vector DBs, embeddings, evals, and python.
        Preferred skills are LLM fine-tuning, learning-to-rank, distributed systems, and NLP/IR.
        """
        mandatory_cols = ['match_vector_db', 'match_embeddings', 'match_evaluation', 'match_python']
        preferred_cols = ['match_llm_finetune', 'match_learning_to_rank', 'match_distributed_systems', 'match_nlp_ir']
        
        # Calculate fraction matches (fallback to 0 if column is missing)
        m_req = sum(df[col].astype(float) if col in df.columns else 0.0 for col in mandatory_cols) / len(mandatory_cols)
        m_pref = sum(df[col].astype(float) if col in df.columns else 0.0 for col in preferred_cols) / len(preferred_cols)
        
        # Mandatory matching gets 70% of skill score, preferred gets 30%
        return 0.7 * m_req + 0.3 * m_pref

    def compute_production_experience_score(self, df):
        """Computes the Production Experience Score.
        Scales with total years of experience up to a threshold of 8 years.
        Academic-only or consulting-only histories are penalized.
        """
        yoe = df['years_of_experience'].fillna(0.0).astype(float)
        exp_score = (yoe / 8.0).clip(0.0, 1.0)
        
        # Build modifiers
        modifier = pd.Series(1.0, index=df.index)
        if 'disq_pure_research' in df.columns:
            modifier = np.where(df['disq_pure_research'], modifier * 0.1, modifier)
        if 'disq_only_consulting' in df.columns:
            modifier = np.where(df['disq_only_consulting'], modifier * 0.7, modifier)
            
        return exp_score * modifier

    def compute_retrieval_ranking_experience_score(self, df):
        """Computes the Retrieval/Ranking Experience Score.
        Rewards specific experience in vector databases, embeddings/dense retrieval, and NLP/IR.
        """
        score = pd.Series(0.0, index=df.index)
        if 'match_vector_db' in df.columns:
            score += np.where(df['match_vector_db'], 0.4, 0.0)
        if 'match_embeddings' in df.columns:
            score += np.where(df['match_embeddings'], 0.4, 0.0)
        if 'match_nlp_ir' in df.columns:
            score += np.where(df['match_nlp_ir'], 0.2, 0.0)
        return score

    def compute_behavioral_score(self, df):
        """Computes the Behavioral Score.
        Factors in recruiter response rate (40%), login recency (30%), 
        interview attendance (20%), and open-to-work flag (10%).
        """
        r_resp = df['recruiter_response_rate'].fillna(0.0).astype(float)
        i_comp = df['interview_completion_rate'].fillna(0.0).astype(float)
        
        # Calculate activity recency (penalty for inactive > 180 days)
        if 'last_active_days_ago' in df.columns:
            days_ago = df['last_active_days_ago'].fillna(-1).astype(float)
            # -1 represents unknown/missing active data
            recency = np.where(days_ago < 0, 0.5, (1.0 - (days_ago / 180.0)).clip(0.1, 1.0))
        else:
            recency = pd.Series(0.5, index=df.index)
            
        o_work = np.where(df['open_to_work_flag'].fillna(False), 1.0, 0.5)
        
        return 0.4 * r_resp + 0.3 * recency + 0.2 * i_comp + 0.1 * o_work

    def compute_startup_fit_score(self, df):
        """Computes Startup Fit Score.
        Reduces score for title chasers/hoppers or consulting-only profiles.
        """
        score = pd.Series(1.0, index=df.index)
        if 'disq_title_chaser' in df.columns:
            score = np.where(df['disq_title_chaser'], score - 0.5, score)
        if 'disq_only_consulting' in df.columns:
            score = np.where(df['disq_only_consulting'], score - 0.4, score)
        return score.clip(0.0, 1.0)

    def compute_risk_penalty(self, df):
        """Computes Risk Penalty.
        Aggregates flags for invalid data or timelines.
        Note: flag_duplicate_identity is excluded from penalties as it is
        primarily a synthetic dataset artifact (generated name collisions).
        It is retained for informational reporting only.
        """
        penalty = pd.Series(0.0, index=df.index)
        if 'flag_chronology_error' in df.columns:
            penalty += np.where(df['flag_chronology_error'], 0.3, 0.0)
        if 'flag_salary_error' in df.columns:
            penalty += np.where(df['flag_salary_error'], 0.3, 0.0)
        if 'flag_trust_error' in df.columns:
            penalty += np.where(df['flag_trust_error'], 0.2, 0.0)
        if 'flag_honeypot_timeline_inflated' in df.columns:
            penalty += np.where(df['flag_honeypot_timeline_inflated'], 0.3, 0.0)
        if 'flag_honeypot_skill_inflated' in df.columns:
            penalty += np.where(df['flag_honeypot_skill_inflated'], 0.3, 0.0)
        if 'flag_honeypot_title_mismatch' in df.columns:
            penalty += np.where(df['flag_honeypot_title_mismatch'], 0.3, 0.0)
        # flag_duplicate_identity excluded: synthetic dataset generation artifact
        return penalty

    def score_dataframe(self, df):
        """Applies the scoring calculations to a DataFrame.
        
        Args:
            df (pd.DataFrame): Flat candidate features DataFrame.
            
        Returns:
            pd.DataFrame: A copy of the DataFrame with sub-scores and final ranking score appended.
        """
        out_df = df.copy()
        
        # Compute sub-score columns
        out_df['score_skill_match'] = self.compute_skill_match_score(df)
        out_df['score_production_experience'] = self.compute_production_experience_score(df)
        out_df['score_retrieval_ranking'] = self.compute_retrieval_ranking_experience_score(df)
        out_df['score_behavioral'] = self.compute_behavioral_score(df)
        out_df['score_startup_fit'] = self.compute_startup_fit_score(df)
        out_df['penalty_risk'] = self.compute_risk_penalty(df)
        
        # Apply weights and subtract risk penalty
        raw_relevance = (
            self.weights['skill_match'] * out_df['score_skill_match'] +
            self.weights['production_experience'] * out_df['score_production_experience'] +
            self.weights['retrieval_ranking'] * out_df['score_retrieval_ranking'] +
            self.weights['behavioral'] * out_df['score_behavioral'] +
            self.weights['startup_fit'] * out_df['score_startup_fit']
        )
        
        # Final Score is raw relevance minus risk penalty (clipped to minimum of 0.0)
        out_df['final_score'] = (raw_relevance - out_df['penalty_risk']).clip(0.0, 1.0)
        
        return out_df
