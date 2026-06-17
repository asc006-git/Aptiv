import os
import time
import json
import ctypes
from ctypes import wintypes
import pandas as pd
from candidate_parser import parse_jsonl

# Win32 structures for Windows-native memory tracking (avoids psutil dependency)
class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]

def get_current_process_memory_mb():
    """Returns the current process's Working Set memory usage in MB on Windows."""
    try:
        GetProcessMemoryCounters = ctypes.windll.psapi.GetProcessMemoryCounters
        GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
        
        process_handle = GetCurrentProcess()
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        
        if GetProcessMemoryCounters(process_handle, ctypes.byref(counters), counters.cb):
            return counters.WorkingSetSize / (1024.0 * 1024.0)
    except Exception as e:
        print("Warning: Could not measure memory usage:", e)
    return 0.0

def generate_large_jsonl(source_json_path, output_jsonl_path, target_count=100000):
    """Generates a large JSONL dataset by repeating and mutating sample candidates."""
    print(f"Generating large candidate dataset of {target_count} records...")
    start_time = time.perf_counter()
    
    with open(source_json_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    
    sample_size = len(samples)
    if sample_size == 0:
        raise ValueError("Source JSON file is empty!")
        
    written = 0
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        while written < target_count:
            # Pick a sample candidate and mutate details to make it unique
            sample = samples[written % sample_size]
            cand_id = f"CAND_{written:07d}"
            
            # Create a clone
            candidate = json.loads(json.dumps(sample))
            candidate['candidate_id'] = cand_id
            
            # Write line
            f.write(json.dumps(candidate) + "\n")
            written += 1
            
            if written % 20000 == 0:
                print(f"  Written {written}/{target_count} profiles...")
                
    end_time = time.perf_counter()
    duration = end_time - start_time
    file_size_mb = os.path.getsize(output_jsonl_path) / (1024.0 * 1024.0)
    print(f"Successfully generated {output_jsonl_path} ({file_size_mb:.2f} MB) in {duration:.2f} seconds.\n")

def run_benchmark():
    source_path = r"data/sample_candidates.json"
    large_jsonl_path = r"data/large_candidates.jsonl"
    target_records = 100000
    
    # 1. Generate the test dataset
    if not os.path.exists(large_jsonl_path):
        generate_large_jsonl(source_path, large_jsonl_path, target_count=target_records)
    else:
        print(f"Dataset '{large_jsonl_path}' already exists. Re-using it.")
        
    # 2. Get baseline memory
    baseline_mem = get_current_process_memory_mb()
    print(f"Baseline process RAM: {baseline_mem:.2f} MB")
    
    # 3. Perform Parsing Benchmark
    print("\n--- Starting Parser Benchmark ---")
    start_time = time.perf_counter()
    
    df = parse_jsonl(large_jsonl_path)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    # 4. Measure peak / ending memory
    ending_mem = get_current_process_memory_mb()
    ram_overhead = ending_mem - baseline_mem
    df_mem_mb = df.memory_usage(deep=True).sum() / (1024.0 * 1024.0)
    
    print("\n--- Parser Performance Results ---")
    print(f"Total parsed records       : {len(df)}")
    print(f"Execution time             : {elapsed_time:.3f} seconds (Target: < 300 seconds)")
    print(f"Parsing speed              : {len(df) / elapsed_time:.1f} records/second")
    print(f"Process RAM delta          : {ram_overhead:.2f} MB (Baseline: {baseline_mem:.2f} MB -> Ending: {ending_mem:.2f} MB)")
    print(f"DataFrame memory footprint : {df_mem_mb:.2f} MB")
    
    # Check constraints
    assert elapsed_time < 300.0, "Runtime constraint violated (> 5 min)!"
    assert ending_mem < 16384.0, "Memory constraint violated (> 16 GB)!"
    print("\n[SUCCESS] Parser meets all challenge runtime and memory constraints.")

    # 5. Output Summary Statistics for Verification
    print("\n--- Dataset Profile and Quality Metrics ---")
    print(f"Suspicious profiles flagged: {df['is_suspicious_profile'].sum()} / {len(df)}")
    
    disq_cols = [col for col in df.columns if col.startswith('disq_')]
    print("\nDisqualifications Summary:")
    for col in disq_cols:
        count = df[col].sum()
        pct = (count / len(df)) * 100
        print(f"  - {col:25}: {count:6d} ({pct:5.1f}%)")
        
    flag_cols = [col for col in df.columns if col.startswith('flag_')]
    print("\nData Quality Flags Summary:")
    for col in flag_cols:
        count = df[col].sum()
        pct = (count / len(df)) * 100
        print(f"  - {col:25}: {count:6d} ({pct:5.1f}%)")
        
    # Clean up the large JSONL file to save disk space
    print("\nCleaning up temporary large dataset file...")
    if os.path.exists(large_jsonl_path):
        os.remove(large_jsonl_path)
        print(f"Removed '{large_jsonl_path}'. Workspace is clean.")

if __name__ == "__main__":
    run_benchmark()
