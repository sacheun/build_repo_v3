#!/usr/bin/env python3
"""All Repositories Copilot Prompt Orchestrator

Runs a multi-repository pipeline in two modes:

    --mode steps    (granular):
      1. /generate-repo-task-checklists input='repositories_small.txt'  (ONCE)
      2. For each tasks/*_repo_checklist.md (alphabetical):
           a. /task-clone-repo clone_path='./clone_repos' checklist_path='tasks/<file>'
           b. /task-find-solutions checklist_path='tasks/<file>'
           c. /generate-solution-task-checklists checklist_path='tasks/<file>'
           d. /task-search-readme checklist_path='tasks/<file>'
           e. /task-scan-readme checklist_path='tasks/<file>'
           f. /task-execute-readme checklist_path='tasks/<file>'

  --mode combine  (condensed):
      1. /generate-repo-task-checklists input='repositories_small.txt'  (ONCE)
      2. For each tasks/*_repo_checklist.md (alphabetical):
           a. /execute-repo-task repo_checklist='tasks/<file>' clone='./clone_repos'

Notes:
- UTF-8 encoding with errors ignored.
- Stops on first failure unless --continue-on-error is provided.
- Produces consolidated summary JSON at ./output/all_repos_pipeline_summary.json
- Non-scriptable tasks are invoked by prompts themselves; this orchestrator only sequences prompt calls.

Usage:
    python tools/run_all_repos.py --mode steps
    python tools/run_all_repos.py --mode combine

Flags:
    --log <path>             Optional log file (default ./output/all_repos_orchestrator.log)
    --continue-on-error      Continue processing other repositories even if a prompt fails
    --mode {steps,combine}   Pipeline style
"""
from __future__ import annotations
import argparse, sys, os, json, datetime
from typing import List, Dict, Tuple

REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TOOLS_DIR = os.path.join(REPO_ROOT, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

try:
    from copilot_executor import CopilotExecutor
    from pipeline_core import execute_pipeline
except ImportError:
    print('[fatal] Unable to import copilot_executor from tools directory.', file=sys.stderr)
    sys.exit(1)

TASKS_DIR = os.path.join(REPO_ROOT, 'tasks')
OUTPUT_DIR = os.path.join(REPO_ROOT, 'output')

STEP_SEQUENCE = [
    ('task-clone-repo', lambda f: {'clone_path': './clone_repos', 'checklist_path': f}),
    ('task-find-solutions', lambda f: {'checklist_path': f}),
    ('generate-solution-task-checklists', lambda f: {'checklist_path': f}),
    ('task-search-readme', lambda f: {'checklist_path': f}),
    ('task-scan-readme', lambda f: {'checklist_path': f}),
    ('task-execute-readme', lambda f: {'checklist_path': f}),
]

COMBINE_SEQUENCE = [
    ('execute-repo-task', lambda f: {'repo_checklist': f, 'clone': './clone_repos'}),
]

def find_repo_checklists() -> List[str]:
    if not os.path.isdir(TASKS_DIR):
        return []
    files = []
    for name in os.listdir(TASKS_DIR):
        if name.endswith('_repo_checklist.md'):
            files.append(os.path.join('tasks', name).replace('\\', '/'))
    return sorted(files)

def run_pipeline(mode: str, log_file: str, continue_on_error: bool) -> int:
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Prepare copilot executor (used for checklist generation only; per-repo pipelines use shared executor logic)
    executor = CopilotExecutor(log_file=log_file, debug=False)
    executor.initialize_log('All Repositories Pipeline Execution Log')

    # Stage 1: Generate repo task checklists once
    print('[stage 1] /generate-repo-task-checklists')
    gen_exit, gen_out, gen_err = executor.execute_prompt(
        prompt_name='generate-repo-task-checklists',
        params={'input': 'repositories_small.txt'}
    )
    if gen_exit != 0:
        print('[error] generate-repo-task-checklists failed; aborting pipeline.')
        summary = {
            'overall_status': 'FAIL',
            'failed_stage': 'generate-repo-task-checklists',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'repos_processed': 0,
            'mode': mode,
        }
        _write_summary(summary)
        return 1

    # Discover repo checklist files AFTER generation
    repo_checklists = find_repo_checklists()
    if not repo_checklists:
        print('[warn] No *_repo_checklist.md files found in tasks directory. Nothing to process.')
        summary = {
            'overall_status': 'SUCCESS',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'repos_processed': 0,
            'mode': mode,
            'details': []
        }
        _write_summary(summary)
        return 0

    print(f'[info] Found {len(repo_checklists)} repository checklist(s).')

    sequence = STEP_SEQUENCE if mode == 'steps' else COMBINE_SEQUENCE
    repo_results: List[Dict] = []
    overall_status = 'SUCCESS'

    for r_index, checklist_path in enumerate(repo_checklists, start=1):
        repo_name = os.path.basename(checklist_path).replace('_repo_checklist.md','')
        print(f"\n[repo {r_index}/{len(repo_checklists)}] Processing {repo_name}")
        per_repo_pipeline = [(prompt, param_fn(checklist_path)) for prompt, param_fn in sequence]
        # Reuse shared execution utility; write individual repo summary to a temp location for trace if needed
        repo_summary_path = os.path.join(OUTPUT_DIR, f"{repo_name}_pipeline_summary.json")
        exit_code, summary = execute_pipeline(
            pipeline=per_repo_pipeline,
            log_file=log_file,
            continue_on_error=continue_on_error,
            step_by_step=(mode == 'steps'),
            mode=mode,
            summary_path=repo_summary_path
        )
        stages = summary.get('pipeline', [])
        if exit_code != 0:
            overall_status = 'FAIL'
            if not continue_on_error:
                print('  [abort] Stopping further processing due to failure.')
        repo_results.append({
            'repo_name': repo_name,
            'checklist_path': checklist_path,
            'stages': stages,
        })
        if overall_status == 'FAIL' and not continue_on_error:
            break

    summary = {
        'overall_status': overall_status,
        'mode': mode,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'repos_processed': len(repo_results),
        'repos_failed': [r for r in repo_results if any(s['stage_status']=='FAIL' for s in r['stages'])],
        'details': repo_results,
    }
    _write_summary(summary)
    print(f"\nPipeline complete. Overall status: {overall_status}. Summary written to ./output/all_repos_pipeline_summary.json")
    try:
        abs_log = os.path.abspath(log_file)
    except Exception:
        abs_log = log_file
    print(f"[log] Detailed execution log available at: {abs_log}")
    return 0 if overall_status == 'SUCCESS' else 1


def _write_summary(summary: Dict) -> None:
    path = os.path.join(OUTPUT_DIR, 'all_repos_pipeline_summary.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', errors='ignore') as f:
        json.dump(summary, f, indent=2)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Multi-repository Copilot prompt orchestrator.')
    p.add_argument('--log', default='./output/all_repos_orchestrator.log', help='Path to log file.')
    p.add_argument('--continue-on-error', action='store_true', help='Continue processing other repositories even if a prompt fails.')
    p.add_argument('--mode', choices=['steps','combine'], default='combine', help="Execution mode: 'steps' granular sequence; 'combine' condensed execute-repo-task.")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    mode = args.mode
    # Normalize log path
    log_file = args.log.replace('\\','/')
    return run_pipeline(mode=mode, log_file=log_file, continue_on_error=args.continue_on_error)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
