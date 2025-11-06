#!/usr/bin/env python3
"""Sequential Copilot Prompt Orchestrator

Executes a fixed pipeline of Copilot prompts for the ic3_spool_cosine-dep-spool repository
in strict sequential order, waiting for each to finish before invoking the next.

Modes:
  --mode all  -> Two-stage automatic pipeline:
      1. /generate-repo-task-checklists input='repositories_small.txt'
      2. /execute-repo-task repo_checklist='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md' clone='./clone_repos'
  --mode step -> Full seven-stage interactive pipeline:
      1. /generate-repo-task-checklists input='repositories_small.txt'
      2. /task-clone-repo clone_path='./clone_repos' checklist_path='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'
      3. /task-search-readme checklist_path='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'
      4. /task-scan-readme checklist_path='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'
      5. /task-execute-readme checklist_path='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'
      6. /task-find-solutions checklist_path='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'
      7. /generate-solution-task-checklists checklist_path='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'

Notes:
- All subprocess calls use UTF-8 encoding (errors='ignore').
- This script does not supply authentication tokens; private repo cloning may fail unless 'copilot' prompt handles auth.
- On non-zero exit code, pipeline stops and prints a concise failure summary.

Usage:
    python tools/run_ic3_spool_cosine-dep-spool.py --mode all
    python tools/run_ic3_spool_cosine-dep-spool.py --mode step

Flags:
    --log <path>             Optional log file (default ./output/orchestrator.log)
    --continue-on-error      If set, will attempt to continue even if a prompt fails.
    --mode {all,step}        Execution style: 'all' runs full pipeline automatically; 'step' asks before each stage.
    --step-by-step           Deprecated alias for --mode step (will be removed). If both provided, 'step' wins.

"""
from __future__ import annotations
import argparse, sys, json, datetime, os
from typing import List, Tuple, Dict

# Ensure relative paths are resolved from repository root
REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TOOLS_DIR = os.path.join(REPO_ROOT, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

try:
    from copilot_executor import CopilotExecutor
except ImportError:
    print('[fatal] Unable to import copilot_executor from tools directory.', file=sys.stderr)
    sys.exit(1)

PIPELINE_STEP = [
    ('generate-repo-task-checklists', {'input': 'repositories_small.txt'}),
    ('task-clone-repo', {'clone_path': './clone_repos', 'checklist_path': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'}),
    ('task-search-readme', {'checklist_path': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'}),
    ('task-scan-readme', {'checklist_path': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'}),
    ('task-execute-readme', {'checklist_path': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'}),
    ('task-find-solutions', {'checklist_path': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'}),
    ('generate-solution-task-checklists', {'checklist_path': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'}),
]

PIPELINE_ALL = [
    ('generate-repo-task-checklists', {'input': 'repositories_small.txt'}),
    ('execute-repo-task', {'repo_checklist': 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md', 'clone': './clone_repos'}),
]

# Default pipeline (will be replaced in main based on mode)
PIPELINE = PIPELINE_STEP

def run_pipeline(log_file: str, continue_on_error: bool, step_by_step: bool, mode: str) -> int:
    executor = CopilotExecutor(log_file=log_file, debug=True)
    executor.initialize_log('IC3 Spool Pipeline Execution Log')

    results: List[Dict[str, str]] = []
    overall_status = 'SUCCESS'

    import sys
    is_tty = sys.stdin.isatty()
    print(f"[mode] Execution mode: {mode} (interactive={step_by_step})")
    for idx, (prompt, params) in enumerate(PIPELINE, start=1):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        print(f"\n[stage {idx}/{len(PIPELINE)}] /{prompt}")
        if step_by_step:
            # Step mode auto-continues; display parameters only.
            print("  Parameters:")
            for k,v in params.items():
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
    summary_path = os.path.join(REPO_ROOT, 'output', 'ic3_spool_pipeline_summary.json')
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8', errors='ignore') as f:
        json.dump({
            'pipeline': [r for r in results],
            'overall_status': overall_status,
            'completed_stages': len(results),
            'failed_stages': [r for r in results if r['stage_status'] == 'FAIL'],
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        }, f, indent=2)
    print(f"\nPipeline complete. Status: {overall_status}. Summary written to {summary_path}")
    return 0 if overall_status == 'SUCCESS' else 1


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Sequential Copilot prompt orchestrator.')
    p.add_argument('--log', default='./output/orchestrator.log', help='Path to log file.')
    p.add_argument('--continue-on-error', action='store_true', help='Continue pipeline despite failures.')
    p.add_argument('--mode', choices=['all','step'], default='all', help="Execution mode: 'all' runs automatically; 'step' prompts before each stage.")
    # Deprecated flag retained for backward compatibility
    p.add_argument('--step-by-step', action='store_true', help='Deprecated: alias for --mode step.')
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    # Determine final mode considering deprecated flag
    mode = args.mode
    if args.step_by_step and mode != 'step':
        print('[warn] --step-by-step is deprecated; overriding --mode to step.')
        mode = 'step'
    step_by_step = (mode == 'step')
    # Select pipeline globally for run_pipeline
    global PIPELINE
    PIPELINE = PIPELINE_ALL if mode == 'all' else PIPELINE_STEP
    # Normalize log path (avoid backslashes)
    log_file = args.log.replace('\\', '/')
    return run_pipeline(log_file=log_file, continue_on_error=args.continue_on_error, step_by_step=step_by_step, mode=mode)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
