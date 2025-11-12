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
    --include-solution       Run per-solution pipelines with retries after each repo
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
    from repo_check_utils import check_repo_readiness
    from solution_check_utils import check_solution_readiness
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


def find_solution_checklists(repo_name: str) -> List[str]:
    """Return sorted list of relative solution checklist paths for a repository."""
    if not os.path.isdir(TASKS_DIR):
        return []
    prefix = f"{repo_name}__"
    results: List[str] = []
    for name in os.listdir(TASKS_DIR):
        if name.endswith('_solution_checklist.md') and name.startswith(prefix):
            results.append(os.path.join('tasks', name).replace('\\', '/'))
    return sorted(results)


def solution_label_from_path(path: str) -> str:
    """Extract a friendly solution label from checklist path."""
    base = os.path.splitext(os.path.basename(path))[0]
    if '__' in base:
        base = base.split('__', 1)[1]
    return base.replace('_solution_checklist', '')


def run_solution_attempts(
    repo_name: str,
    pass_index: int,
    mode: str,
    continue_on_error: bool,
    base_log_dir: str,
    base_stem: str,
    base_ext: str
) -> Tuple[Dict[str, Dict], bool]:
    """Execute per-solution pipelines with retries; return details and aggregate readiness."""
    solution_paths = find_solution_checklists(repo_name)
    if not solution_paths:
        print(f"    [repo:{repo_name}] solution phase: no solution checklist files found.")
        return {}, True

    results: Dict[str, Dict] = {}
    all_ready = True
    max_attempts = 3
    step_by_step = (mode == 'steps')

    for rel_path in solution_paths:
        sol_label = solution_label_from_path(rel_path)
        sol_key = sol_label
        results[sol_key] = {
            'checklist_path': rel_path,
            'attempts': [],
            'final_readiness': 'PENDING'
        }
        abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(REPO_ROOT, rel_path.replace('/', os.sep))
        for attempt in range(1, max_attempts + 1):
            print(f"    [repo:{repo_name}] [solution:{sol_label}] attempt {attempt}/{max_attempts}")
            log_file = os.path.join(
                base_log_dir,
                f"{base_stem}_{repo_name}_{sol_label}_pass{pass_index}_attempt{attempt}{base_ext}"
            )
            summary_path = os.path.join(
                OUTPUT_DIR,
                f"{os.path.splitext(os.path.basename(rel_path))[0]}_summary_pass{pass_index}_attempt{attempt}.json"
            )
            if mode == 'combine':
                sol_pipeline = [('execute-solution-task', {'solution_checklist': rel_path, 'clone': './clone_repos'})]
            else:
                sol_pipeline = [
                    ('task-restore-solution', {'solution_checklist': rel_path}),
                    ('task-build-solution', {'solution_checklist': rel_path})
                ]
            exit_code, sol_summary = execute_pipeline(
                pipeline=sol_pipeline,
                log_file=log_file,
                continue_on_error=continue_on_error,
                step_by_step=step_by_step,
                mode=mode,
                summary_path=summary_path
            )
            ready = check_solution_readiness(abs_path)
            attempt_record = {
                'attempt': attempt,
                'exit_code': exit_code,
                'readiness': 'PASS' if ready else 'FAIL',
                'stages': sol_summary.get('pipeline', []),
                'log_file': os.path.abspath(log_file)
            }
            results[sol_key]['attempts'].append(attempt_record)
            if ready:
                results[sol_key]['final_readiness'] = 'PASS'
                print(f"    [repo:{repo_name}] [solution:{sol_label}] readiness PASS after attempt {attempt}.")
                break
            else:
                results[sol_key]['final_readiness'] = 'FAIL'
                if attempt < max_attempts:
                    print(f"    [repo:{repo_name}] [solution:{sol_label}] readiness FAIL; retrying (next attempt {attempt+1}/{max_attempts}).")
        if results[sol_key]['final_readiness'] != 'PASS':
            all_ready = False
    return results, all_ready

def run_pipeline(mode: str, log_file: str, continue_on_error: bool, include_solution: bool) -> int:
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
    # Prepare base log stem for per-repo, per-pass logging
    base_log_dir = os.path.dirname(log_file) or '.'
    base_log_name = os.path.basename(log_file)
    if '.' in base_log_name:
        base_stem, base_ext = base_log_name.rsplit('.', 1)
        base_ext = '.' + base_ext
    else:
        base_stem, base_ext = base_log_name, '.log'
    os.makedirs(base_log_dir, exist_ok=True)
    overall_status = 'SUCCESS'
    # Global attempt loop: run all repos each pass, verify, and retry failing ones up to 3 passes.
    max_passes = 3
    pass_index = 1
    repo_state: Dict[str, Dict] = {os.path.basename(p).replace('_repo_checklist.md',''): {
        'checklist_path': p,
        'attempts': [],
        'final_readiness': 'PENDING'
    } for p in repo_checklists}

    while pass_index <= max_passes:
        print(f"\n[global-pass {pass_index}/{max_passes}] Starting pipeline pass across repositories")
        any_pending = False
        for repo_name, state in repo_state.items():
            if state['final_readiness'] == 'PASS':
                continue  # Skip already passing repos
            any_pending = True
            checklist_path = state['checklist_path']
            per_repo_pipeline = [(prompt, param_fn(checklist_path)) for prompt, param_fn in sequence]
            repo_summary_path = os.path.join(OUTPUT_DIR, f"{repo_name}_pipeline_summary_pass{pass_index}.json")
            # Derive per-repo, per-pass log file
            repo_log_file = os.path.join(base_log_dir, f"{base_stem}_{repo_name}_pass{pass_index}{base_ext}")
            print(f"  [repo:{repo_name}] executing pipeline (pass {pass_index}) log={repo_log_file}")
            exit_code, summary = execute_pipeline(
                pipeline=per_repo_pipeline,
                log_file=repo_log_file,
                continue_on_error=continue_on_error,
                step_by_step=(mode == 'steps'),
                mode=mode,
                summary_path=repo_summary_path
            )
            stages = summary.get('pipeline', [])
            full_checklist_path = os.path.join(REPO_ROOT, checklist_path.replace('/', os.sep)) if not checklist_path.startswith(REPO_ROOT) else checklist_path
            print(f"    [repo:{repo_name}] readiness verification ...")
            ready = check_repo_readiness(full_checklist_path)
            attempt_record = {
                'pass': pass_index,
                'exit_code': exit_code,
                'repo_readiness': 'PASS' if ready else 'FAIL',
                'stages': stages,
                'log_file': os.path.abspath(repo_log_file)
            }

            solutions_all_ready = True
            solution_results: Dict[str, Dict] = {}
            if include_solution and not (exit_code != 0 and not continue_on_error):
                solution_results, solutions_all_ready = run_solution_attempts(
                    repo_name=repo_name,
                    pass_index=pass_index,
                    mode=mode,
                    continue_on_error=continue_on_error,
                    base_log_dir=base_log_dir,
                    base_stem=base_stem,
                    base_ext=base_ext
                )
                attempt_record['solution_readiness'] = 'PASS' if solutions_all_ready else 'FAIL'
                attempt_record['solutions'] = solution_results
                solutions_container = state.setdefault('solutions', {})
                for sol_label, sol_data in solution_results.items():
                    sol_entry = solutions_container.setdefault(sol_label, {
                        'checklist_path': sol_data['checklist_path'],
                        'attempts': [],
                        'final_readiness': 'PENDING'
                    })
                    sol_entry['checklist_path'] = sol_data['checklist_path']
                    sol_entry['attempts'].extend(sol_data['attempts'])
                    sol_entry['final_readiness'] = sol_data['final_readiness']
            elif include_solution:
                attempt_record['solution_readiness'] = 'SKIPPED'
                attempt_record['solutions'] = {}
                state.setdefault('solutions', {})
                solutions_all_ready = False if exit_code != 0 else True

            combined_ready = ready and (solutions_all_ready if include_solution else True)
            attempt_record['combined_readiness'] = 'PASS' if combined_ready else 'FAIL'
            state['attempts'].append(attempt_record)

            print(f"    [repo:{repo_name}] repo readiness {'PASS' if ready else 'FAIL'}.")
            if include_solution:
                label = attempt_record['solution_readiness']
                if label == 'PASS':
                    print(f"    [repo:{repo_name}] solutions readiness PASS.")
                elif label == 'FAIL':
                    print(f"    [repo:{repo_name}] solutions readiness FAIL.")
                else:
                    print(f"    [repo:{repo_name}] solutions readiness SKIPPED (pipeline aborted).")

            if exit_code != 0 and not continue_on_error:
                overall_status = 'FAIL'
                print(f"    [repo:{repo_name}] aborting global passes due to failure and continue-on-error disabled.")
                state['final_readiness'] = 'FAIL'
                any_pending = False
                break

            if combined_ready:
                state['final_readiness'] = 'PASS'
                print(f"    [repo:{repo_name}] overall readiness PASS.")
            else:
                state['final_readiness'] = 'FAIL' if pass_index == max_passes else 'PENDING'
                msg = 'overall readiness FAIL'
                if state['final_readiness'] == 'PENDING':
                    msg += ' (will retry if passes remain).'
                print(f"    [repo:{repo_name}] {msg}")
        if not any_pending:
            break
        # If all repos passed early, break
        if all(s['final_readiness'] == 'PASS' for s in repo_state.values()):
            print("[global-pass] All repositories passed readiness early; stopping further passes.")
            break
        pass_index += 1

    repo_results: List[Dict] = []
    for name, state in repo_state.items():
        repo_results.append({
            'repo_name': name,
            'checklist_path': state['checklist_path'],
            'attempts': state['attempts'],
            'final_readiness': state['final_readiness'],
            'solutions': state.get('solutions', {})
        })

    if any(r['final_readiness'] != 'PASS' for r in repo_results):
        overall_status = 'FAIL'

    # Final readiness verification across all processed repositories
    readiness_pass = sum(1 for r in repo_results if r['final_readiness'] == 'PASS')
    readiness_fail = [r['repo_name'] for r in repo_results if r['final_readiness'] != 'PASS']

    print(f"\n[readiness] {readiness_pass}/{len(repo_results)} repository checklists passed mandatory variable/task readiness after global passes.")
    if readiness_fail:
        print(f"[readiness] Still failing after {min(max_passes, pass_index)} pass(es): {readiness_fail}")

    def _has_failed_stage(repo_entry: Dict) -> bool:
        for attempt in repo_entry.get('attempts', []):
            for stage in attempt.get('stages', []):
                if stage.get('stage_status') == 'FAIL':
                    return True
            for sol in attempt.get('solutions', {}).values():
                for sol_attempt in sol.get('attempts', []):
                    for stage in sol_attempt.get('stages', []):
                        if stage.get('stage_status') == 'FAIL':
                            return True
        return False

    all_log_files: List[str] = []
    for repo_entry in repo_results:
        for attempt in repo_entry.get('attempts', []):
            all_log_files.append(attempt['log_file'])
            for sol in attempt.get('solutions', {}).values():
                for sol_attempt in sol.get('attempts', []):
                    all_log_files.append(sol_attempt['log_file'])

    summary = {
        'overall_status': overall_status,
        'mode': mode,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'repos_processed': len(repo_results),
        'repos_failed': [r for r in repo_results if _has_failed_stage(r)],
        'repos_readiness_pass': readiness_pass,
        'repos_readiness_fail': readiness_fail,
        'details': repo_results,
        'log_files': all_log_files
    }
    _write_summary(summary)
    print(f"\nPipeline complete. Overall status: {overall_status}. Summary written to ./output/all_repos_pipeline_summary.json")
    print("[log] Per-repo pass log files:")
    for lf in summary['log_files']:
        print(f"  - {lf}")
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
    p.add_argument('--include-solution', action='store_true', help='Execute per-solution pipelines with retries after each repository.')
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    mode = args.mode
    # Normalize log path
    log_file = args.log.replace('\\','/')
    return run_pipeline(
        mode=mode,
        log_file=log_file,
        continue_on_error=args.continue_on_error,
        include_solution=args.include_solution
    )

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
