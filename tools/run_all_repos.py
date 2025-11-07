#!/usr/bin/env python3
"""All Repositories Copilot Prompt Orchestrator.

Runs a multi-repository pipeline in two modes.

Mode ``steps`` (granular):
    1. /generate-repo-task-checklists input='repositories_small.txt' (once)
    2. For each ``tasks/*_repo_checklist.md`` in alphabetical order:
        a. /task-clone-repo clone_path='./clone_repos'
           checklist_path='tasks/<file>'
         b. /task-find-solutions checklist_path='tasks/<file>'
         c. /generate-solution-task-checklists checklist_path='tasks/<file>'
         d. /task-search-readme checklist_path='tasks/<file>'
         e. /task-scan-readme checklist_path='tasks/<file>'
         f. /task-execute-readme checklist_path='tasks/<file>'

Mode ``combine`` (condensed):
    1. /generate-repo-task-checklists input='repositories_small.txt' (once)
    2. For each ``tasks/*_repo_checklist.md`` in alphabetical order:
        a. /execute-repo-task repo_checklist='tasks/<file>'
           clone='./clone_repos'

Notes:
    - UTF-8 encoding with errors ignored.
    - Stops on first failure unless ``--continue-on-error`` is provided.
    - Produces summary JSON at ``./output/all_repos_pipeline_summary.json``.
    - Prompts handle non-scriptable steps; this orchestrator sequences calls.

Usage::

    python tools/run_all_repos.py --mode steps
    python tools/run_all_repos.py --mode combine

Flags:
    --log <path>             Optional log
                             (default ./output/all_repos_orchestrator.log)
    --continue-on-error      Continue other repositories after a prompt failure
    --mode {steps,combine}   Pipeline style
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from typing import Dict, List

REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TOOLS_DIR = os.path.join(REPO_ROOT, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

try:
    from copilot_executor import CopilotExecutor
    from pipeline_core import execute_pipeline
    from repo_check_utils import check_repo_readiness
except ImportError:
    print(
        '[fatal] Unable to import copilot_executor from tools directory.',
        file=sys.stderr
    )
    sys.exit(1)

TASKS_DIR = os.path.join(REPO_ROOT, 'tasks')
OUTPUT_DIR = os.path.join(REPO_ROOT, 'output')

STEP_SEQUENCE = [
    (
        'task-clone-repo',
        lambda path: {'clone_path': './clone_repos', 'checklist_path': path}
    ),
    ('task-find-solutions', lambda path: {'checklist_path': path}),
    (
        'generate-solution-task-checklists',
        lambda path: {'checklist_path': path}
    ),
    ('task-search-readme', lambda path: {'checklist_path': path}),
    ('task-scan-readme', lambda path: {'checklist_path': path}),
    ('task-execute-readme', lambda path: {'checklist_path': path}),
]

COMBINE_SEQUENCE = [
    (
        'execute-repo-task',
        lambda path: {'repo_checklist': path, 'clone': './clone_repos'}
    ),
]


def find_repo_checklists() -> List[str]:
    if not os.path.isdir(TASKS_DIR):
        return []
    files = []
    for name in os.listdir(TASKS_DIR):
        if name.endswith('_repo_checklist.md'):
            files.append(os.path.join('tasks', name).replace('\\', '/'))
    return sorted(files)


_CHECKLISTS_GENERATED_THIS_RUN = False


def run_pipeline(mode: str, log_file: str, continue_on_error: bool) -> int:
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Prepare executor (checklist generation only; per-repo pipelines share)
    executor = CopilotExecutor(log_file=log_file, debug=False)
    executor.initialize_log('All Repositories Pipeline Execution Log')

    global _CHECKLISTS_GENERATED_THIS_RUN
    if not _CHECKLISTS_GENERATED_THIS_RUN:
        # Stage 1: Generate repo task checklists once per script execution
        print('[stage 1] /generate-repo-task-checklists')
        gen_exit, gen_out, gen_err = executor.execute_prompt(
            prompt_name='generate-repo-task-checklists',
            params={'input': 'repositories_small.txt'}
        )
        if gen_exit != 0:
            print(
                '[error] generate-repo-task-checklists failed; aborting '
                'pipeline.'
            )
            summary = {
                'overall_status': 'FAIL',
                'failed_stage': 'generate-repo-task-checklists',
                'timestamp': datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(timespec='seconds'),
                'repos_processed': 0,
                'mode': mode,
            }
            _write_summary(summary)
            return 1
        _CHECKLISTS_GENERATED_THIS_RUN = True
    else:
        print('[stage 1] Skipping /generate-repo-task-checklists '
              '(already executed this run)')

    # Discover repo checklist files AFTER generation
    repo_checklists = find_repo_checklists()
    if not repo_checklists:
        print('[warn] No *_repo_checklist.md files found in tasks directory. '
              'Nothing to process.')
        summary = {
            'overall_status': 'SUCCESS',
            'timestamp': datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(timespec='seconds'),
            'repos_processed': 0,
            'mode': mode,
            'details': []
        }
        _write_summary(summary)
        return 0

    print(f'[info] Found {len(repo_checklists)} repository checklist(s).')

    sequence = STEP_SEQUENCE if mode == 'steps' else COMBINE_SEQUENCE
    overall_status = 'SUCCESS'
    # Global attempt loop: run all repos, verify, retry failing ones (max 3)
    max_passes = 3
    pass_index = 1
    repo_state: Dict[str, Dict] = {
        os.path.basename(path).replace('_repo_checklist.md', ''): {
            'checklist_path': path,
            'attempts': [],
            'final_readiness': 'PENDING'
        }
        for path in repo_checklists
    }

    while pass_index <= max_passes:
        print(
            f"\n[global-pass {pass_index}/{max_passes}] Starting pipeline "
            "pass across repositories"
        )
        any_pending = False
        for repo_name, state in repo_state.items():
            if state['final_readiness'] == 'PASS':
                continue  # Skip already passing repos
            any_pending = True
            checklist_path = state['checklist_path']
            per_repo_pipeline = [
                (prompt, param_fn(checklist_path))
                for prompt, param_fn in sequence
            ]
            repo_summary_filename = (
                f"{repo_name}_pipeline_summary_pass{pass_index}.json"
            )
            repo_summary_path = os.path.join(
                OUTPUT_DIR,
                repo_summary_filename
            )
            print(
                f"  [repo:{repo_name}] executing pipeline "
                f"(pass {pass_index})"
            )
            exit_code, summary = execute_pipeline(
                pipeline=per_repo_pipeline,
                log_file=log_file,
                continue_on_error=continue_on_error,
                step_by_step=(mode == 'steps'),
                mode=mode,
                summary_path=repo_summary_path
            )
            stages = summary.get('pipeline', [])
            if checklist_path.startswith(REPO_ROOT):
                full_checklist_path = checklist_path
            else:
                normalized = checklist_path.replace('/', os.sep)
                full_checklist_path = os.path.join(REPO_ROOT, normalized)
            print(f"    [repo:{repo_name}] readiness verification ...")
            ready = check_repo_readiness(full_checklist_path)
            state['attempts'].append({
                'pass': pass_index,
                'exit_code': exit_code,
                'readiness': 'PASS' if ready else 'FAIL',
                'stages': stages
            })
            if exit_code != 0 and not continue_on_error:
                overall_status = 'FAIL'
                print(
                    f"    [repo:{repo_name}] aborting global passes due to "
                    "failure and continue-on-error disabled."
                )
                # Mark as failed readiness to surface
                state['final_readiness'] = 'FAIL'
                any_pending = False  # Force loop exit
                break
            if ready:
                state['final_readiness'] = 'PASS'
                print(f"    [repo:{repo_name}] readiness PASS.")
            else:
                state['final_readiness'] = (
                    'FAIL' if pass_index == max_passes else 'PENDING'
                )
                print(
                    f"    [repo:{repo_name}] readiness FAIL "
                    "(will retry if passes remain)."
                )
        if not any_pending:
            break

        failing_repos = [
            name for name, state in repo_state.items()
            if state['final_readiness'] != 'PASS'
        ]
        if failing_repos:
            joined = ', '.join(failing_repos)
            print(
                f"[missing-steps] Repositories requiring retry: {joined}"
            )
        else:
            print('[missing-steps] All repositories completed required steps.')

        # If all repos passed early, break
        if all(s['final_readiness'] == 'PASS' for s in repo_state.values()):
            print('[global-pass] All repositories passed readiness early; '
                  'stopping further passes.')
            break
        pass_index += 1
        if pass_index <= max_passes and failing_repos:
            print(
                f"[retry] Initiating pass {pass_index} for repositories with "
                "missing steps."
            )

    repo_results: List[Dict] = []
    for name, state in repo_state.items():
        repo_results.append({
            'repo_name': name,
            'checklist_path': state['checklist_path'],
            'attempts': state['attempts'],
            'final_readiness': state['final_readiness']
        })

    if any(r['final_readiness'] != 'PASS' for r in repo_results):
        overall_status = 'FAIL'

    # Final readiness verification across all processed repositories
    readiness_pass = sum(
        1 for r in repo_results if r['final_readiness'] == 'PASS'
    )
    readiness_fail = [
        r['repo_name'] for r in repo_results
        if r['final_readiness'] != 'PASS'
    ]

    print(
        f"\n[readiness] {readiness_pass}/{len(repo_results)} repository "
        "checklists passed mandatory variable/task readiness after global "
        "passes."
    )
    if readiness_fail:
        remaining = ', '.join(readiness_fail)
        print(
            f"[readiness] Still failing after {min(max_passes, pass_index)} "
            f"pass(es): {remaining}"
        )

    def _has_failed_stage(repo_entry: Dict) -> bool:
        for attempt in repo_entry.get('attempts', []):
            for stage in attempt.get('stages', []):
                if stage.get('stage_status') == 'FAIL':
                    return True
        return False

    summary = {
        'overall_status': overall_status,
        'mode': mode,
        'timestamp': datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec='seconds'),
        'repos_processed': len(repo_results),
        'repos_failed': [r for r in repo_results if _has_failed_stage(r)],
        'repos_readiness_pass': readiness_pass,
        'repos_readiness_fail': readiness_fail,
        'details': repo_results,
    }
    _write_summary(summary)
    print(
        f"\nPipeline complete. Overall status: {overall_status}. Summary "
        "written to ./output/all_repos_pipeline_summary.json"
    )
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
    p = argparse.ArgumentParser(
        description='Multi-repository Copilot prompt orchestrator.'
    )
    p.add_argument(
        '--log',
        default='./output/all_repos_orchestrator.log',
        help='Path to log file.'
    )
    p.add_argument(
        '--continue-on-error',
        action='store_true',
        help=(
            'Continue processing other repositories even if a prompt fails.'
        )
    )
    p.add_argument(
        '--mode',
        choices=['steps', 'combine'],
        default='combine',
        help=(
            "Execution mode: 'steps' granular sequence; 'combine' condensed "
            'execute-repo-task.'
        )
    )
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    mode = args.mode
    # Normalize log path
    log_file = args.log.replace('\\', '/')
    return run_pipeline(
        mode=mode,
        log_file=log_file,
        continue_on_error=args.continue_on_error
    )


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
