#!/usr/bin/env python3
"""Sequential Copilot Prompt Orchestrator

Executes a fixed pipeline of Copilot prompts for the ic3_spool_cosine-dep-spool repository
in strict sequential order, waiting for each to finish before invoking the next.

Modes:
        --mode combine -> Two-stage automatic pipeline:
      1. /generate-repo-task-checklists input='repositories_small.txt'
      2. /execute-repo-task repo_checklist='tasks/ic3_spool_cosine-dep-spool_repo_checklist.md' clone='./clone_repos'
    --mode steps -> Full seven-stage interactive pipeline:
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
    python tools/run_single_file.py --mode combine
    python tools/run_single_file.py --mode steps

Flags:
    --log <path>             Optional log file (default ./output/orchestrator.log)
    --continue-on-error      If set, will attempt to continue even if a prompt fails.
    --mode {combine,steps}   Execution style: 'combine' runs full pipeline automatically; 'steps' asks before each stage.

"""
from __future__ import annotations
import argparse, sys, json, datetime, os, shutil, glob, re
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

DEFAULT_CHECKLIST = 'tasks/ic3_spool_cosine-dep-spool_repo_checklist.md'


def build_repo_pipelines(checklist_path: str) -> tuple[List[tuple], List[tuple]]:
    """Construct repository pipeline definitions for the provided checklist."""
    repo_pipeline_step = [
        ('task-generate-repo-task-checklists', {'input': 'repositories_small.txt'}),
        ('task-clone-repo', {'clone_path': './clone_repos', 'checklist_path': checklist_path}),
        ('task-find-solutions', {'checklist_path': checklist_path}),
        ('task-generate-solution-task-checklists', {'checklist_path': checklist_path}),
        ('task-search-readme', {'checklist_path': checklist_path}),
        ('task-scan-readme', {'checklist_path': checklist_path}),
        ('task-execute-readme', {'checklist_path': checklist_path})
    ]

    repo_pipeline_all = [
        ('task-generate-repo-task-checklists', {'input': 'repositories_small.txt'}),
        ('execute-repo-task', {'repo_checklist': checklist_path}),
    ]
    return repo_pipeline_step, repo_pipeline_all


def build_solution_pipelines(checklist_path: str) -> tuple[List[tuple], List[tuple]]:
    """Construct solution pipeline definitions for the provided checklist."""
    solution_pipeline_step = [
        ('task-restore-solutions', {'solution_checklist_path': checklist_path}),
        ('task-build-solutions', {'solution_checklist_path': checklist_path}),
        ('task-verify-build-artifacts', {'solution_checklist_path': checklist_path}),
    ]

    solution_pipeline_all = [
        ('execute-solution-task', {'solution_checklist': checklist_path}),
    ]
    return solution_pipeline_step, solution_pipeline_all

from pipeline_core import execute_pipeline
from repo_check_utils import check_repo_readiness
from solution_check_utils import check_solution_readiness
# Removed solution-level execution; include-solution option deprecated.

def purge_state_directories(log_file: str) -> None:
    """Remove stateful directories for a clean slate before pipeline runs."""
    purge_targets = ['output', 'temp-script', 'tasks']
    for rel in purge_targets:
        target_path = os.path.join(REPO_ROOT, rel)
        if os.path.isdir(target_path):
            try:
                shutil.rmtree(target_path)
                print(f"[purge] Removed directory: {rel}")
            except Exception as e:
                print(f"[purge-warn] Failed to remove {rel}: {e}")
        elif os.path.exists(target_path):
            print(f"[purge-warn] Path exists but is not directory, skipping: {rel}")
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.isdir(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"[warn] Could not create log directory {log_dir}: {e}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Sequential Copilot prompt orchestrator.')
    p.add_argument('--log', default='./output/orchestrator.log', help='Path to log file.')
    p.add_argument('--continue-on-error', action='store_true', help='Continue pipeline despite failures.')
    p.add_argument('--mode', choices=['combine','steps'], default='combine', help="Execution mode: 'combine' runs automatically; 'steps' prompts before each stage.")
    p.add_argument('--checklist', default=DEFAULT_CHECKLIST, help='Path to the repository checklist to drive the pipeline.')
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    mode = args.mode
    checklist_path = args.checklist.replace('\\', '/')
    readiness_checker = None
    checklist_label = 'repository'
    if 'repo_checklist.md' in checklist_path:
        pipeline_step, pipeline_all = build_repo_pipelines(checklist_path)
        readiness_checker = check_repo_readiness
        checklist_label = 'repository'
    elif 'solution_checklist' in checklist_path:
        pipeline_step, pipeline_all = build_solution_pipelines(checklist_path)
        readiness_checker = check_solution_readiness
        checklist_label = 'solution'
    else:
        print(f"[fatal] Unsupported checklist path: {checklist_path}")
        return 1
    if readiness_checker is None:
        print(f"[fatal] No readiness checker available for checklist: {checklist_path}")
        return 1
    step_by_step = (mode == 'steps')
    # Normalize base log path (avoid backslashes); we'll derive per-attempt file names
    base_log_path = args.log.replace('\\', '/')
    # Purge using base path (original behavior)
    purge_state_directories(base_log_path)

    selected_pipeline = pipeline_all if mode == 'combine' else pipeline_step
    # Track discovered solution checklist files (used for readiness verification)
    # Solution-level handling removed (include-solution deprecated)

    attempt = 1
    max_attempts = 3
    repo_name = os.path.splitext(os.path.basename(checklist_path))[0]
    last_exit_code = None
    per_attempt_logs: List[str] = []
    ready = False

    # Derive filename pattern: <stem>_attempt<N><ext>
    base_dir = os.path.dirname(base_log_path) or '.'
    base_file = os.path.basename(base_log_path)
    if '.' in base_file:
        stem, ext = base_file.rsplit('.', 1)
        ext = '.' + ext
    else:
        stem, ext = base_file, '.log'

    os.makedirs(base_dir, exist_ok=True)

    # Phase 1: Repo attempts (original behavior)
    while attempt <= max_attempts:
        attempt_log_file = os.path.join(base_dir, f"{stem}_attempt{attempt}{ext}")
        attempt_summary_path = os.path.join(REPO_ROOT, 'output', f'single_file_pipeline_summary_attempt{attempt}.json')
        print(f"[pipeline] Attempt {attempt}/{max_attempts}")
        print(f"[log] Writing Copilot execution log to: {attempt_log_file}")
        last_exit_code, _summary = execute_pipeline(
            pipeline=[(p, params) for p, params in selected_pipeline],
            log_file=attempt_log_file,
            continue_on_error=args.continue_on_error,
            step_by_step=step_by_step,
            mode=mode,
            summary_path=attempt_summary_path
        )
        per_attempt_logs.append(os.path.abspath(attempt_log_file))
        print(f"[verification] Checking {checklist_label} readiness (attempt {attempt}) ...")
        ready = readiness_checker(os.path.join(REPO_ROOT, checklist_path))
        if ready:
            print(f"[verification] {checklist_label.capitalize()} readiness success after attempt {attempt}.")
            break
        if attempt < max_attempts:
            print(f"[retry] Will rerun pipeline (next attempt: {attempt+1}/{max_attempts}).")
        attempt += 1

    if attempt > max_attempts and not ready:
        print(f"[verification] Final {checklist_label} readiness: FAIL after {max_attempts} attempts.")

    # Phase 2 removed: solution attempts deprecated with removal of include-solution flag.

    # Combined final summary
    repo_status = 'OK' if ready else 'FAIL'
    print(f"[final readiness] {checklist_label}={repo_status}")
    if ready:
        print(f"[final readiness detail] {checklist_label}s OK: [{repo_name}]")
    else:
        print(f"[final readiness detail] {checklist_label}s FAIL: [{repo_name}]")

    print("[log] Attempt log files:")
    for path in per_attempt_logs:
        print(f"  - {path}")

    # Return last exit code (or 1 if none captured)
    return last_exit_code if last_exit_code is not None else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
