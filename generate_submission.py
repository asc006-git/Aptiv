import json
import time
import logging
import argparse
import sys
from pathlib import Path

import pandas as pd

from candidate_parser import parse_jsonl
from scorer import CandidateScorer
from narrative_generator import generate_candidate_narratives
from hidden_gem_detector import detect_hidden_gems
from rap_engine import compute_rap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def is_jsonl(path: Path) -> bool:
    return path.suffix.lower() == ".jsonl"


def load_json_candidates(json_path: Path) -> list:
    logger.info(f"Loading JSON candidates from {json_path}")
    start = time.perf_counter()
    with open(json_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    elapsed = time.perf_counter() - start
    logger.info(f"Loaded {len(candidates)} candidates in {elapsed:.3f}s")
    return candidates


def write_jsonl(candidates: list, output_path: Path) -> None:
    logger.info(f"Writing JSONL to {output_path}")
    start = time.perf_counter()
    with open(output_path, "w", encoding="utf-8") as f:
        for cand in candidates:
            f.write(json.dumps(cand) + "\n")
    elapsed = time.perf_counter() - start
    logger.info(f"JSONL written in {elapsed:.3f}s")


def validate_dataframe(df: pd.DataFrame, stage: str) -> None:
    if df.empty:
        raise ValueError(f"{stage}: DataFrame is empty")
    if "candidate_id" not in df.columns:
        raise ValueError(f"{stage}: Missing required column 'candidate_id'")
    logger.info(f"{stage} validation passed: {len(df)} rows, {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")


def run_pipeline(input_path: Path, output_csv: Path, temp_jsonl: Path) -> pd.DataFrame:
    total_start = time.perf_counter()

    if is_jsonl(input_path):
        logger.info(f"Detected JSONL input: {input_path}")
        jsonl_path = input_path
        use_temp = False
    else:
        logger.info(f"Detected JSON input: {input_path}")
        candidates = load_json_candidates(input_path)
        write_jsonl(candidates, temp_jsonl)
        jsonl_path = temp_jsonl
        use_temp = True

    logger.info("Parsing candidates...")
    parse_start = time.perf_counter()
    df = parse_jsonl(str(jsonl_path))
    parse_time = time.perf_counter() - parse_start
    logger.info(f"Parsed {len(df)} candidates in {parse_time:.3f}s")

    validate_dataframe(df, "Post-parse")

    logger.info("Scoring candidates...")
    score_start = time.perf_counter()
    scorer = CandidateScorer()
    scored_df = scorer.score_dataframe(df)
    score_time = time.perf_counter() - score_start
    logger.info(f"Scored {len(scored_df)} candidates in {score_time:.3f}s")

    validate_dataframe(scored_df, "Post-score")

    if "final_score" not in scored_df.columns:
        raise ValueError("Scoring failed: 'final_score' column missing")

    logger.info("Ranking candidates...")
    scored_df = scored_df.sort_values(["final_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
    scored_df["rank"] = range(1, len(scored_df) + 1)

    logger.info("Detecting Hidden Gems...")
    hg_start = time.perf_counter()
    scored_df = detect_hidden_gems(scored_df)
    hg_time = time.perf_counter() - hg_start
    hg_count = scored_df['is_hidden_gem'].sum()
    logger.info(f"Detected {hg_count} Hidden Gems out of {len(scored_df)} candidates in {hg_time:.3f}s")

    logger.info("Computing RAP scores...")
    rap_start = time.perf_counter()
    scored_df = compute_rap(scored_df)
    rap_time = time.perf_counter() - rap_start
    logger.info(f"Computed RAP scores in {rap_time:.3f}s")

    logger.info("Generating candidate narratives & assigning tiers...")
    narrative_start = time.perf_counter()
    scored_df = generate_candidate_narratives(scored_df)
    narrative_time = time.perf_counter() - narrative_start
    logger.info(f"Generated narratives in {narrative_time:.3f}s")

    # Collect available columns for the submission view
    narrative_cols = ["candidate_id", "rank", "final_score",
                      "archetype", "action_recommendation",
                      "narrative_tier", "display_tier",
                      "narrative", "positive_signals", "concerns",
                      "jd_sentence",
                      "narrative_strengths", "narrative_risks",
                      "narrative_behavioral", "narrative_recruitability",
                      "strength_sources", "risk_sources",
                      "hidden_gem_score", "is_hidden_gem", "hidden_gem_category",
                      "hidden_gem_narrative",
                      "rap_score", "rap_priority", "rap_action", "rap_rationale"]
    available = [c for c in narrative_cols if c in scored_df.columns]
    submission = scored_df[available].copy()
    submission = submission.rename(columns={"final_score": "score"})

    validate_dataframe(submission, "Submission")

    logger.info(f"Saving submission to {output_csv}")
    export_df = submission.head(100).copy()
    export_df["reasoning"] = export_df["narrative"]
    export_df[["candidate_id", "rank", "score", "reasoning"]].to_csv(output_csv, index=False)
    logger.info(f"Submission saved: {len(export_df)} rows (top 100 + reasoning)")

    total_time = time.perf_counter() - total_start
    logger.info(f"Total pipeline time: {total_time:.3f}s")

    mem_mb = scored_df.memory_usage(deep=True).sum() / 1024**2
    logger.info(f"Final DataFrame memory footprint: {mem_mb:.2f} MB")

    return submission, total_time, mem_mb


def main():
    parser = argparse.ArgumentParser(description="Generate candidate ranking submission")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/sample_candidates.json"),
        help="Path to input candidate file (.json or .jsonl)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("submission.csv"),
        help="Path to output submission CSV",
    )
    parser.add_argument(
        "--temp-jsonl",
        type=Path,
        default=Path("data/temp_candidates.jsonl"),
        help="Path to temporary JSONL file (used only for JSON input)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Number of top candidates to display",
    )
    args = parser.parse_args()

    try:
        if not args.input.exists():
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)

        args.temp_jsonl.parent.mkdir(parents=True, exist_ok=True)
        args.output.parent.mkdir(parents=True, exist_ok=True)

        submission, total_time, mem_mb = run_pipeline(args.input, args.output, args.temp_jsonl)

        print("\n" + "=" * 100)
        print(f"TOP {args.top_k} CANDIDATES")
        print("=" * 100)
        top_k = submission.head(args.top_k)
        for _, row in top_k.iterrows():
            display_tier = row.get('display_tier', row.get('narrative_tier', ''))
            arch = row.get('archetype', '')
            act = row.get('action_recommendation', '')
            print(f"Rank {row['rank']:3d} | {row['candidate_id']:>12} | Score: {row['score']:.6f}")
            print(f"  Tier: {display_tier} | Archetype: {arch} | Action: {act}")
            if 'positive_signals' in row and isinstance(row['positive_signals'], list) and row['positive_signals']:
                print(f"  Signals: {'; '.join(row['positive_signals'][:3])}")
            if 'concerns' in row and isinstance(row['concerns'], list) and row['concerns']:
                print(f"  Concerns: {'; '.join(row['concerns'][:2])}")
            print(f"  {row['narrative']}")
            print("-" * 100)
        print("=" * 100)

        print("\n" + "=" * 60)
        print("PIPELINE SUMMARY")
        print("=" * 60)
        print(f"  Candidates processed : {len(submission)}")
        print(f"  Total runtime        : {total_time:.3f}s")
        print(f"  DataFrame memory     : {mem_mb:.2f} MB")
        print(f"  Output path          : {args.output.resolve()}")
        print("=" * 60)

        if 'is_hidden_gem' in submission.columns:
            hg_count = submission['is_hidden_gem'].sum()
            print(f"\nHIDDEN GEMS: {hg_count} / {len(submission)}")
            hg_cats = submission[submission['is_hidden_gem']]['hidden_gem_category'].value_counts()
            for cat, count in hg_cats.items():
                print(f"  {cat}: {count}")
            print()
            top_hg = submission[submission['is_hidden_gem']].head(5)
            for _, row in top_hg.iterrows():
                print(f"  Rank {row['rank']:4d} | {row['candidate_id']} | HG Score: {row['hidden_gem_score']:.1f} | {row['hidden_gem_category']}")

        if 'rap_priority' in submission.columns:
            print(f"\nRAP DISTRIBUTION")
            rap_dist = submission['rap_priority'].value_counts()
            for cat, count in rap_dist.items():
                pct = count / len(submission) * 100
                print(f"  {cat:25s}: {count:5d} ({pct:5.1f}%)")
            print()
            top_rap = submission.sort_values('rap_score', ascending=False).head(10)
            for _, row in top_rap.iterrows():
                print(f"  RAP {row['rap_score']:5.1f} | {row['candidate_id']} | FS: {row['score']:.4f} | {row['rap_priority']}")
                print(f"  {row['rap_action']}")
                print()

        if args.temp_jsonl.exists():
            args.temp_jsonl.unlink()
            logger.info("Cleaned up temporary JSONL file")

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()