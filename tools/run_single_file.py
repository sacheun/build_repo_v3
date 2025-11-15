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
import argparse, sys, json, datetime, os, shutil, glob, re, stat
from typing import List, Tuple, Dict, Optional, Callable

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

def build_repo_pipelines(checklist_path: str) -> tuple[List[tuple], List[tuple]]:
    """Construct repository pipeline definitions for the provided checklist."""
    repo_pipeline_step = [
        ('task-clone-repo', {'clone_path': './clone_repos', 'checklist_path': checklist_path}),
        ('task-find-solutions', {'checklist_path': checklist_path}),
        ('task-generate-solution-task-checklists', {'checklist_path': checklist_path}),
        ('task-search-readme', {'checklist_path': checklist_path}),
        ('task-scan-readme', {'checklist_path': checklist_path}),
        ('task-execute-readme', {'checklist_path': checklist_path})
    ]

    repo_pipeline_all = [
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


def normalize_checklist_path(path: str) -> str:
    """Return a repository-relative checklist path with forward slashes."""
    normalized = path.replace('\\', '/')
    if os.path.isabs(normalized):
        normalized = os.path.relpath(normalized, REPO_ROOT)
    normalized = normalized.replace('\\', '/')
    return normalized


def sanitize_slug(name: str) -> str:
    """Produce a filesystem-safe slug for log file naming."""
    slug = re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-')
    return slug.lower() or 'checklist'


def colorize(message: str, *, status: Optional[str] = None) -> str:
    """Return a colorized message when stdout is a TTY."""
    if not sys.stdout.isatty():
        return message
    colors = {
        'OK': '\033[32m',  # green
        'FAIL': '\033[31m',  # red
    }
    reset = '\033[0m'
    prefix = colors.get(status)
    if prefix:
        return f"{prefix}{message}{reset}"
    return message


def execute_initial_tasks(
    initial_pipeline: List[Tuple[str, Dict[str, str]]],
    *,
    args: argparse.Namespace,
    mode: str,
    step_by_step: bool,
    base_dir: str,
    stem: str,
    ext: str,
    per_attempt_logs: List[str],
) -> int:
    """Run the bootstrap pipeline before main checklist processing."""
    if not initial_pipeline:
        return 0
    initial_log_file = os.path.join(base_dir, f"{stem}_initial{ext}")
    initial_summary = os.path.join(REPO_ROOT, 'output', 'initial_pipeline_summary.json')
    os.makedirs(os.path.dirname(initial_summary), exist_ok=True)
    print("[pipeline] Running initial tasks prior to main pipeline ...")
    print(f"[log] Writing Copilot execution log to: {initial_log_file}")
    exit_code, _ = execute_pipeline(
        pipeline=[(prompt, params) for prompt, params in initial_pipeline],
        log_file=initial_log_file,
        continue_on_error=args.continue_on_error,
        step_by_step=step_by_step,
        mode=mode,
        summary_path=initial_summary,
    )
    per_attempt_logs.append(os.path.abspath(initial_log_file))
    return exit_code


def run_pipeline_for_checklist(
    checklist_path: str,
    *,
    args: argparse.Namespace,
    mode: str,
    step_by_step: bool,
    base_dir: str,
    stem: str,
    ext: str,
    per_attempt_logs: List[str],
    pipeline_step: List[Tuple[str, Dict[str, str]]],
    pipeline_all: List[Tuple[str, Dict[str, str]]],
    readiness_checker: Callable[[str], bool],
    checklist_label: str,
) -> Tuple[bool, Optional[int]]:
    """Execute the appropriate pipeline for a given checklist and verify readiness."""
    selected_pipeline = pipeline_all if mode == 'combine' else pipeline_step
    slug = sanitize_slug(os.path.splitext(os.path.basename(checklist_path))[0])
    attempt = 1
    max_attempts = 3
    ready = False
    last_exit_code: Optional[int] = None
    fs_checklist_path = (
        checklist_path
        if os.path.isabs(checklist_path)
        else os.path.join(REPO_ROOT, checklist_path)
    )
    while attempt <= max_attempts:
        attempt_log_file = os.path.join(base_dir, f"{stem}_{slug}_attempt{attempt}{ext}")
        summary_filename = f"single_file_pipeline_summary_{slug}_attempt{attempt}.json"
        attempt_summary_path = os.path.join(REPO_ROOT, 'output', summary_filename)
        os.makedirs(os.path.dirname(attempt_summary_path), exist_ok=True)
        print(f"[pipeline] {checklist_label.capitalize()} checklist {slug}: attempt {attempt}/{max_attempts}")
        print(f"[log] Writing Copilot execution log to: {attempt_log_file}")
        last_exit_code, _summary = execute_pipeline(
            pipeline=[(prompt, params) for prompt, params in selected_pipeline],
            log_file=attempt_log_file,
            continue_on_error=args.continue_on_error,
            step_by_step=step_by_step,
            mode=mode,
            summary_path=attempt_summary_path,
        )
        per_attempt_logs.append(os.path.abspath(attempt_log_file))
        print(f"[verification] Checking {checklist_label} readiness for {slug} (attempt {attempt}) ...")
        ready = readiness_checker(fs_checklist_path)
        if ready:
            print(
                f"[verification] {checklist_label.capitalize()} readiness success for {slug} after attempt {attempt}."
            )
            break
        if attempt < max_attempts:
            print(
                f"[retry] Will rerun pipeline for {slug} (next attempt: {attempt + 1}/{max_attempts})."
            )
        attempt += 1
    if attempt > max_attempts and not ready:
        print(
            f"[verification] Final {checklist_label} readiness for {slug}: FAIL after {max_attempts} attempts."
        )
    repo_name = os.path.splitext(os.path.basename(checklist_path))[0]
    status = 'OK' if ready else 'FAIL'
    final_message = f"[final readiness] {checklist_label}={status} [{repo_name}]"
    print(colorize(final_message, status=status))
    return ready, last_exit_code

def _handle_remove_readonly(func: Callable[[str], None], path: str, exc: tuple) -> None:
    """Best-effort removal helper for read-only files on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as err:  # pragma: no cover - diagnostic logging only
        print(f"[purge-warn] Unable to force remove {path}: {err}")


def purge_state_directories(log_file: str, *, remove_output: bool = True, remove_tasks: bool = True) -> None:
    """Remove stateful directories for a clean slate before pipeline runs."""
    purge_targets: List[str] = []
    if remove_output:
        purge_targets.append('output')
    purge_targets.append('temp-script')
    if remove_tasks:
        purge_targets.append('tasks')
    for rel in purge_targets:
        target_path = os.path.join(REPO_ROOT, rel)
        try:
            if os.path.isdir(target_path):
                shutil.rmtree(target_path, onerror=_handle_remove_readonly)
                print(f"[purge] Removed directory: {rel}")
            elif os.path.exists(target_path):
                os.remove(target_path)
                print(f"[purge] Removed file: {rel}")
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"[purge-warn] Failed to remove {rel}: {e}")
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
    p.add_argument('--checklist', help='Path to the repository or solution checklist to drive the pipeline.')
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    mode = args.mode
    step_by_step = (mode == 'steps')
    base_log_path = args.log.replace('\\', '/')
    base_dir = os.path.dirname(base_log_path) or '.'
    base_file = os.path.basename(base_log_path)
    if '.' in base_file:
        stem, ext = base_file.rsplit('.', 1)
        ext = '.' + ext
    else:
        stem, ext = base_file, '.log'
    os.makedirs(base_dir, exist_ok=True)
    per_attempt_logs: List[str] = []

    if args.checklist:
        checklist_path = normalize_checklist_path(args.checklist)
        is_repo = 'repo_checklist.md' in checklist_path
        is_solution = 'solution_checklist' in checklist_path
        purge_state_directories(
            base_log_path,
            remove_output=not is_solution,
            remove_tasks=is_repo,
        )

        readiness_checker: Optional[Callable[[str], bool]] = None
        pipeline_step: List[Tuple[str, Dict[str, str]]] = []
        pipeline_all: List[Tuple[str, Dict[str, str]]] = []
        label = 'repository' if is_repo else 'solution'

        if is_repo:
            initial_pipeline = [('task-generate-repo-task-checklists', {'input': 'repositories_small.txt'})]
            init_exit = execute_initial_tasks(
                initial_pipeline,
                args=args,
                mode=mode,
                step_by_step=step_by_step,
                base_dir=base_dir,
                stem=stem,
                ext=ext,
                per_attempt_logs=per_attempt_logs,
            )
            if init_exit != 0 and not args.continue_on_error:
                print(f"[fatal] Initial pipeline failed with exit code {init_exit}.")
                print("[log] Attempt log files:")
                for path in per_attempt_logs:
                    print(f"  - {path}")
                return init_exit
            pipeline_step, pipeline_all = build_repo_pipelines(checklist_path)
            readiness_checker = check_repo_readiness
        elif is_solution:
            pipeline_step, pipeline_all = build_solution_pipelines(checklist_path)
            readiness_checker = check_solution_readiness
        else:
            print(f"[fatal] Unsupported checklist path: {checklist_path}")
            return 1

        fs_checklist_path = (
            checklist_path if os.path.isabs(checklist_path) else os.path.join(REPO_ROOT, checklist_path)
        )
        if not os.path.exists(fs_checklist_path):
            print(f"[fatal] Checklist not found: {fs_checklist_path}")
            return 1
        ready, last_exit_code = run_pipeline_for_checklist(
            checklist_path,
            args=args,
            mode=mode,
            step_by_step=step_by_step,
            base_dir=base_dir,
            stem=stem,
            ext=ext,
            per_attempt_logs=per_attempt_logs,
            pipeline_step=pipeline_step,
            pipeline_all=pipeline_all,
            readiness_checker=readiness_checker,
            checklist_label=label,
        )
        print("[log] Attempt log files:")
        for path in per_attempt_logs:
            print(f"  - {path}")
        if last_exit_code is not None:
            return last_exit_code
        return 0 if ready else 1

    # No checklist specified: process all repo and solution checklists sequentially.
    purge_state_directories(base_log_path, remove_output=True, remove_tasks=True)
    initial_pipeline = [('task-generate-repo-task-checklists', {'input': 'repositories_small.txt'})]
    initial_exit = execute_initial_tasks(
        initial_pipeline,
        args=args,
        mode=mode,
        step_by_step=step_by_step,
        base_dir=base_dir,
        stem=stem,
        ext=ext,
        per_attempt_logs=per_attempt_logs,
    )
    overall_ready = (initial_exit == 0)
    overall_exit = 0 if initial_exit == 0 else initial_exit or 1
    if initial_exit != 0 and not args.continue_on_error:
        print(f"[fatal] Initial pipeline failed with exit code {initial_exit}.")
        print("[log] Attempt log files:")
        for path in per_attempt_logs:
            print(f"  - {path}")
        return initial_exit

    repo_checklists = sorted(glob.glob(os.path.join(REPO_ROOT, 'tasks', '*_repo_checklist.md')))
    repo_checked = 0
    repo_passed = 0
    repo_failed = 0
    if not repo_checklists:
        print("[warn] No repository checklists found to process.")
    for repo_file in repo_checklists:
        rel_path = normalize_checklist_path(repo_file)
        pipeline_step, pipeline_all = build_repo_pipelines(rel_path)
        ready, last_exit_code = run_pipeline_for_checklist(
            rel_path,
            args=args,
            mode=mode,
            step_by_step=step_by_step,
            base_dir=base_dir,
            stem=stem,
            ext=ext,
            per_attempt_logs=per_attempt_logs,
            pipeline_step=pipeline_step,
            pipeline_all=pipeline_all,
            readiness_checker=check_repo_readiness,
            checklist_label='repository',
        )
        repo_checked += 1
        if ready:
            repo_passed += 1
        else:
            repo_failed += 1
        if not ready:
            overall_ready = False
        if last_exit_code is not None and last_exit_code != 0:
            overall_exit = last_exit_code
        elif last_exit_code is None and not ready:
            overall_exit = overall_exit or 1

    # After repo processing, discover solution checklists (which may have been generated).
    solution_checklists = sorted(glob.glob(os.path.join(REPO_ROOT, 'tasks', '*_solution_checklist.md')))
    solution_checked = 0
    solution_passed = 0
    solution_failed = 0
    if not solution_checklists:
        print("[info] No solution checklists found to process.")
    for solution_file in solution_checklists:
        rel_path = normalize_checklist_path(solution_file)
        pipeline_step, pipeline_all = build_solution_pipelines(rel_path)
        ready, last_exit_code = run_pipeline_for_checklist(
            rel_path,
            args=args,
            mode=mode,
            step_by_step=step_by_step,
            base_dir=base_dir,
            stem=stem,
            ext=ext,
            per_attempt_logs=per_attempt_logs,
            pipeline_step=pipeline_step,
            pipeline_all=pipeline_all,
            readiness_checker=check_solution_readiness,
            checklist_label='solution',
        )
        solution_checked += 1
        if ready:
            solution_passed += 1
        else:
            solution_failed += 1
        if not ready:
            overall_ready = False
        if last_exit_code is not None and last_exit_code != 0:
            overall_exit = last_exit_code
        elif last_exit_code is None and not ready:
            overall_exit = overall_exit or 1

    print("[log] Attempt log files:")
    for path in per_attempt_logs:
        print(f"  - {path}")

    print("[summary] Repository readiness: {}/{} passed ({} failed)".format(
        repo_passed,
        repo_checked,
        repo_failed,
    ))
    print("[summary] Solution readiness: {}/{} passed ({} failed)".format(
        solution_passed,
        solution_checked,
        solution_failed,
    ))

    if overall_ready:
        return overall_exit if overall_exit else 0
    return overall_exit or 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
