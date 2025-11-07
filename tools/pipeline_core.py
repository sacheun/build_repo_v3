#!/usr/bin/env python3
"""Pipeline Core Utilities

Provides shared functionality to execute a sequence of Copilot prompts as a pipeline
with consistent logging and summary output.

Function:
    execute_pipeline(pipeline, log_file, continue_on_error, step_by_step, mode, summary_path)

Parameters:
    pipeline: List of tuples (prompt_name, params_dict) to execute in order.
    log_file: Path to log file for CopilotExecutor.
    continue_on_error: If True, continue executing remaining prompts after a failure.
    step_by_step: If True, display parameters for each stage (interactive verbosity).
    mode: String describing execution mode (passed through to summary for traceability).
    summary_path: Path to write JSON summary. If None, summary is not written.

Return:
    (exit_code, summary_dict) where exit_code is 0 on success and >0 on failure.
"""
from __future__ import annotations
import os, json, datetime
from typing import List, Tuple, Dict, Optional

# Dynamic import to avoid circular path issues
try:
    from copilot_executor import CopilotExecutor
except ImportError:
    # Allow relative execution if path not yet injected
    raise

UTC = datetime.timezone.utc

def execute_pipeline(
    pipeline: List[Tuple[str, Dict[str, str]]],
    log_file: str,
    continue_on_error: bool,
    step_by_step: bool,
    mode: str,
    summary_path: Optional[str]
) -> Tuple[int, Dict]:
    """Execute a linear sequence of Copilot prompts and produce a structured summary."""
    executor = CopilotExecutor(log_file=log_file, debug=False)
    executor.initialize_log('Pipeline Execution Log')

    results: List[Dict] = []
    overall_status = 'SUCCESS'

    print(f"[mode] Execution mode: {mode}")
    for idx, (prompt, params) in enumerate(pipeline, start=1):
        ts = datetime.datetime.now(UTC).isoformat(timespec='seconds')
        print(f"\n[stage {idx}/{len(pipeline)}] /{prompt}")
        if step_by_step:
            print("  Parameters:")
            for k, v in params.items():
                print(f"    - {k} = {v}")
        print(f"[execute] Executing /{prompt} ...")
        exit_code, stdout, stderr = executor.execute_prompt(prompt_name=prompt, params=params)
        stage_status = 'SUCCESS' if exit_code == 0 else 'FAIL'
        results.append({
            'order': idx,
            'prompt': prompt,
            'params': params,
            'exit_code': exit_code,
            'timestamp': ts,
            'stage_status': stage_status,
            'stdout_excerpt': (stdout[:400] if stdout else ''),
            'stderr_excerpt': (stderr[:400] if stderr else ''),
        })
        if exit_code != 0:
            print(f"[error] Prompt /{prompt} failed (exit_code={exit_code}).")
            overall_status = 'FAIL'
            if not continue_on_error:
                break
            else:
                print('[warn] continue-on-error enabled; proceeding to next prompt.')

    summary = {
        'pipeline': results,
        'overall_status': overall_status,
        'completed_stages': len(results),
        'failed_stages': [r for r in results if r['stage_status'] == 'FAIL'],
        'timestamp': datetime.datetime.now(UTC).isoformat(timespec='seconds'),
        'mode': mode,
    }

    if summary_path:
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(summary, f, indent=2)
        print(f"\nPipeline summary written to {summary_path}")

    exit_code_final = 0 if overall_status == 'SUCCESS' else 1
    return exit_code_final, summary

__all__ = ['execute_pipeline']
