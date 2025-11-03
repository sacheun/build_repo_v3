#!/usr/bin/env python3
"""
Orchestrate Repository Workflow

This script orchestrates the complete repository workflow by:
1. Generating repository checklists from repositories_small.txt
2. Verifying checklist format
3. Finding all incomplete repository checklists
4. Executing tasks for each repository sequentially
5. Updating master checklist
6. Verifying all tasks completed
7. Processing solution checklists (regardless of repository task completion status)

Note: Solution processing will proceed even when repository tasks are incomplete.

Usage:
    python ./tools/orchestrate_repo_workflow.py [--append]

Environment Variables:
    DEBUG=1  Enable verbose debug logging
"""

import argparse
import csv
import datetime
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

# Import custom modules
from copilot_executor import CopilotExecutor
from repo_operations import RepoOperations
from solution_operations import SolutionOperations

# Global configuration
DEBUG = os.environ.get('DEBUG', '0') == '1'
TASKS_DIR = Path('./tasks')
OUTPUT_DIR = Path('./output')
RESULTS_DIR = Path('./results')
TOOLS_DIR = Path('./tools')
CLONE_DIR = Path('./clone_repos')
TEMP_SCRIPT_DIR = Path('./temp-script')
LOG_FILE = Path('./orchestrate_repo_workflow.log')
MAX_REPO_ATTEMPTS = 3
MAX_SOLUTION_ATTEMPTS = 3

# Initialize Copilot executor and operations
copilot = CopilotExecutor(log_file=LOG_FILE, debug=DEBUG)
repo_ops = RepoOperations(
    tasks_dir=TASKS_DIR,
    output_dir=OUTPUT_DIR,
    results_dir=RESULTS_DIR,
    copilot_executor=copilot,
    debug=DEBUG
)
solution_ops = SolutionOperations(
    tasks_dir=TASKS_DIR,
    results_dir=RESULTS_DIR,
    copilot_executor=copilot,
    debug=DEBUG
)


def debug_print(message: str):
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        print(f"[debug][orchestrate-repo-workflow] {message}")


def clean_directories():
    """Remove files from results, tasks, output, and temp-script dirs."""
    debug_print("cleaning results, tasks, output, temp-script directories")

    for directory in [RESULTS_DIR, TASKS_DIR, OUTPUT_DIR, TEMP_SCRIPT_DIR]:
        if directory.exists():
            file_count = 0
            dir_count = 0
            for item in directory.iterdir():
                if item.is_file():
                    item.unlink()
                    file_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    dir_count += 1
            
            if file_count > 0 or dir_count > 0:
                debug_print(f"  {directory.name}: removed {file_count} files, {dir_count} directories")
    
    debug_print("directory cleanup complete")


def ensure_solution_results_csv():
    """Create solution results tracking files with expected headers when missing."""
    RESULTS_DIR.mkdir(exist_ok=True)

    templates = {
        'solution-results.csv': 'timestamp,repo_name,solution_name,task_name,status,symbol\n',
        'solution_result.csv': 'repo,solution,task name,status\n'
    }

    created_files: List[str] = []

    for filename, header in templates.items():
        csv_path = RESULTS_DIR / filename
        if csv_path.exists():
            continue

        with open(csv_path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(header)

        created_files.append(filename)

    if created_files:
        debug_print(
            (
                "initialized solution results tracking files: {files}"
            ).format(files=', '.join(created_files))
        )


def ensure_repo_results_csv():
    """Create repo_result.csv with expected header when missing."""
    RESULTS_DIR.mkdir(exist_ok=True)

    headers = 'repo,task name,status\n'
    created_files: List[str] = []

    for filename in ('repo_result.csv', 'repo-results.csv'):
        csv_path = RESULTS_DIR / filename
        if csv_path.exists():
            continue

        with open(csv_path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(headers)

        created_files.append(filename)

    if created_files:
        debug_print(
            (
                "initialized repo results tracking files: {files}"
            ).format(files=', '.join(created_files))
        )


def iter_repo_results_files() -> List[Path]:
    """Return candidate repo results CSV files (supports legacy names)."""
    return [
        RESULTS_DIR / 'repo_result.csv',
        RESULTS_DIR / 'repo-results.csv'
    ]


def iter_solution_results_files() -> List[Path]:
    """Return candidate solution results CSV files (supports legacy names)."""
    return [
        RESULTS_DIR / 'solution-results.csv',
        RESULTS_DIR / 'solution_result.csv'
    ]


def purge_repo_results(repo_name: str) -> int:
    """Remove existing repo_result rows for a repository prior to retry."""
    total_removed = 0

    for csv_path in iter_repo_results_files():
        if not csv_path.exists():
            continue

        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as infile:
                reader = csv.reader(infile)
                rows = list(reader)
        except Exception as exc:  # noqa: BLE001
            debug_print(
                f"WARNING: unable to read {csv_path.name} for purge: {exc}"
            )
            continue

        if not rows:
            continue

        header = rows[0]
        data_rows = rows[1:]
        filtered_rows = [header]
        removed_here = 0
        for fields in data_rows:
            if not fields:
                filtered_rows.append(fields)
                continue

            if len(fields) >= 2:
                repo_value = fields[1].strip()
            else:
                repo_value = fields[0].strip()

            if repo_value == repo_name:
                removed_here += 1
                continue

            filtered_rows.append(fields)

        if removed_here:
            try:
                with open(csv_path, 'w', encoding='utf-8', newline='') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows(filtered_rows)
            except Exception as exc:  # noqa: BLE001
                debug_print(
                    f"WARNING: failed to rewrite {csv_path.name}: {exc}"
                )
                continue

            total_removed += removed_here
            debug_print(
                (
                    "purged {count} repo_result rows for {repo} from {name}"
                ).format(
                    count=removed_here,
                    repo=repo_name,
                    name=csv_path.name
                )
            )

    if total_removed == 0:
        debug_print(
            f"no existing repo_result rows found for {repo_name}"
        )

    return total_removed


def run_copilot_command(command: str) -> Tuple[int, str, str]:
    """
    Execute a copilot command using the CopilotExecutor.
    Logs all output to orchestrate_repo_workflow.log

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    return copilot.execute_command(command)

# ============================================================================
# REFACTORED: Repository and solution operation functions moved to modules
# - repo_operations.py: RepoOperations class
# - solution_operations.py: SolutionOperations class
# ============================================================================


def purge_solution_results(repo_name: str, solution_names: Iterable[str]) -> int:
    """Remove rows for a repo/solution pair from solution results CSV files."""
    normalized_repo = (repo_name or '').strip()
    if not normalized_repo:
        debug_print("purge_solution_results skipped - repo name empty")
        return 0

    name_candidates: Set[str] = set()
    for value in solution_names:
        if not value:
            continue
        trimmed = value.strip()
        if not trimmed:
            continue
        name_candidates.add(trimmed)
        name_candidates.add(trimmed.replace('_', ' '))
        name_candidates.add(trimmed.replace('_', '.'))
        name_candidates.add(trimmed.replace('.', '_'))

    normalized_solutions = {name.lower() for name in name_candidates if name}
    if not normalized_solutions:
        debug_print(
            f"purge_solution_results skipped - no solution identifiers for repo {repo_name}"
        )
        return 0

    total_removed = 0

    for csv_path in iter_solution_results_files():
        if not csv_path.exists():
            continue

        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as infile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                rows = list(reader)
        except Exception as exc:  # noqa: BLE001
            debug_print(
                f"WARNING: unable to read {csv_path.name} for purge: {exc}"
            )
            continue

        if not fieldnames:
            continue

        filtered_rows = []
        removed_here = 0

        for row in rows:
            repo_value = (
                row.get('repo')
                or row.get('repo_name')
                or row.get('Repository')
                or ''
            ).strip()
            solution_value = (
                row.get('solution')
                or row.get('solution_name')
                or row.get('Solution')
                or ''
            ).strip()

            if (
                repo_value.lower() == normalized_repo.lower()
                and solution_value.lower() in normalized_solutions
            ):
                removed_here += 1
                continue

            filtered_rows.append(row)

        if removed_here:
            try:
                with open(csv_path, 'w', encoding='utf-8', newline='') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(filtered_rows)
            except Exception as exc:  # noqa: BLE001
                debug_print(
                    f"WARNING: failed to rewrite {csv_path.name}: {exc}"
                )
                continue

            total_removed += removed_here
            debug_print(
                (
                    "purged {count} solution_result rows for {repo}/{solution} "
                    "from {name}"
                ).format(
                    count=removed_here,
                    repo=repo_name,
                    solution='|'.join(sorted(normalized_solutions)),
                    name=csv_path.name
                )
            )

    if total_removed == 0:
        debug_print(
            f"no existing solution_result rows found for {repo_name}"
        )

    return total_removed


def initialize_workflow(append_mode: bool, solutions_only: bool, repo_only: bool) -> datetime.datetime:
    """
    Initialize workflow logging and directories.
    
    Args:
        append_mode: Whether to preserve existing files
        solutions_only: Whether to skip repository processing
        repo_only: Whether to skip solution processing
        
    Returns:
        Start time of the workflow
    """
    start_time = datetime.datetime.now(datetime.timezone.utc)
    
    # Initialize log file
    copilot.initialize_log(
        f"Orchestrate Repository Workflow Log\n"
        f"Started: {start_time.isoformat()}\n"
        f"Append Mode: {append_mode}\n"
        f"Solutions Only: {solutions_only}\n"
        f"Repo Only: {repo_only}"
    )
    
    # Clean directories if append=false and not solutions_only
    if not append_mode and not solutions_only:
        clean_directories()
    else:
        if append_mode:
            debug_print("preserving existing files (append=true)")
        if solutions_only:
            debug_print("solutions_only mode: preserving existing files")
    
    # Ensure directories exist
    for directory in [TASKS_DIR, OUTPUT_DIR, RESULTS_DIR, TOOLS_DIR]:
        directory.mkdir(exist_ok=True)
    
    ensure_solution_results_csv()
    ensure_repo_results_csv()
    
    return start_time


def process_repositories(append_mode: bool) -> Tuple[List[Dict[str, Any]], int, int, int, List[Dict[str, Any]]]:
    """
    Process all repository tasks with retry logic.
    
    Args:
        append_mode: Whether to preserve existing files
        
    Returns:
        Tuple of (repository_details, successful_count, failed_count, total_repositories, final_incomplete_repos)
    """
    repository_details = []
    
    # Step 3: Generate repository checklists
    if not repo_ops.generate_task_checklists('repositories_small.txt', append_mode):
        raise RuntimeError("Failed to generate repository task checklists")
    
    # Step 3a: Verify repository checklist format
    if not repo_ops.verify_checklist_format():
        raise RuntimeError("Repository checklist format verification failed")
    
    # Step 4-6: Discover incomplete repositories
    incomplete_repos = repo_ops.discover_incomplete()
    
    # Count total repositories
    all_checklist_files = list(TASKS_DIR.glob('*_repo_checklist.md'))
    total_repositories = len([
        f for f in all_checklist_files
        if f.name != 'all_repository_checklist.md'
    ])
    
    if not incomplete_repos:
        debug_print("All repositories already complete")
        return [], 0, 0, total_repositories, []
    
    # Step 7: Process repositories with retries
    processed_repo_names: Set[str] = set()
    successful_repo_names: Set[str] = set()
    final_incomplete_map: Dict[str, Dict[str, Any]] = {}
    
    pending_repos: List[Dict[str, Any]] = list(incomplete_repos)
    repo_attempt = 1
    
    while pending_repos and repo_attempt <= MAX_REPO_ATTEMPTS:
        debug_print(
            f"processing {len(pending_repos)} repositories "
            f"(attempt {repo_attempt}/{MAX_REPO_ATTEMPTS})"
        )
        
        next_pending: List[Dict[str, Any]] = []
        
        for repo in pending_repos:
            repo_name = repo['repo_name']
            checklist_path = repo['checklist_path']
            processed_repo_names.add(repo_name)
            
            result_detail = repo_ops.execute_task(
                repo_name,
                checklist_path,
                "./clone_repos"
            )
            result_detail['attempt'] = repo_attempt
            repository_details.append(result_detail)
            
            if result_detail['execution_status'] == 'SUCCESS':
                successful_repo_names.add(repo_name)
        
        verification_results = repo_ops.verify_tasks_completed()
        if isinstance(verification_results, list):
            incomplete_map = {
                item['repo_name']: item
                for item in verification_results
                if isinstance(item, dict) and 'repo_name' in item
            }
        else:
            incomplete_map = {}
        
        for repo in pending_repos:
            repo_name = repo['repo_name']
            if repo_name in incomplete_map:
                if repo_attempt < MAX_REPO_ATTEMPTS:
                    retry_entry = incomplete_map[repo_name]
                    purge_repo_results(repo_name)
                    repo_ops.reset_tasks(
                        retry_entry['checklist_path'],
                        retry_entry.get('incomplete_tasks', [])
                    )
                    next_pending.append(retry_entry)
                else:
                    final_incomplete_map[repo_name] = incomplete_map[repo_name]
                    successful_repo_names.discard(repo_name)
            else:
                successful_repo_names.add(repo_name)
        
        if next_pending:
            retry_names = [
                entry.get('repo_name')
                for entry in next_pending
                if entry.get('repo_name')
            ]
            debug_print(
                "will retry repositories: {names}".format(
                    names=", ".join(sorted(retry_names))
                )
            )

        # Wait 30 minutes after first attempt before retrying
        if repo_attempt == 1 and next_pending:
            wait_seconds = 30 * 60  # 30 minutes
            debug_print(
                f"first attempt completed. waiting {wait_seconds // 60} minutes "
                f"before retry attempt..."
            )
            time.sleep(wait_seconds)
            debug_print("wait completed. starting retry attempt")
        
        pending_repos = next_pending
        repo_attempt += 1
    
    final_incomplete_repos = list(final_incomplete_map.values())
    final_incomplete_names = set(final_incomplete_map.keys())
    
    if processed_repo_names:
        successful_count = len([
            name for name in successful_repo_names
            if name not in final_incomplete_names
        ])
        failed_repo_names = (
            (processed_repo_names - successful_repo_names)
            | final_incomplete_names
        )
        failed_count = len(failed_repo_names)
    else:
        successful_count = 0
        failed_count = 0
    
    return repository_details, successful_count, failed_count, total_repositories, final_incomplete_repos


def build_repos_with_solutions() -> Set[str]:
    """
    Build set of repository names that have solution checklists to process.
    
    Returns:
        Set of repository names with solutions
    """
    repos_with_solutions = set()
    repo_results_contents: List[str] = []
    
    for candidate in iter_repo_results_files():
        if not candidate.exists():
            continue
        
        try:
            with open(candidate, 'r', encoding='utf-8') as handle:
                content = handle.read()
                repo_results_contents.append(content)
                if DEBUG:
                    debug_print(f"Scanning {candidate.name} for task-find-solutions entries")
        except Exception as exc:  # noqa: BLE001
            debug_print(f"WARNING: unable to read {candidate.name} for solutions lookup: {exc}")
    
    if repo_results_contents:
        csv_content = "\n".join(repo_results_contents)
        
        if DEBUG:
            debug_print("Searching for task-find-solutions entries in repo results CSV")
            debug_print(f"CSV content length: {len(csv_content)} bytes")
        
        pattern_all = r'[^|,]+[|,]([^|,]+)[|,]task-find-solutions[|,]'
        all_matches = re.findall(pattern_all, csv_content)
        
        if DEBUG:
            debug_print(f"Found {len(all_matches)} task-find-solutions entries total")
        
        for name in all_matches:
            repo_name = name.strip()
            repos_with_solutions.add(repo_name)
            if DEBUG:
                debug_print(f"Repository '{repo_name}' has task-find-solutions entry")
        
        pattern_with_count = (
            r'[^|,]+[|,]([^|,]+)[|,]task-find-solutions[|,](\d+) solutions?[|,]'
        )
        count_matches = re.findall(pattern_with_count, csv_content)
        
        if DEBUG and count_matches:
            debug_print("Repositories with solution counts:")
            for name, solution_count in count_matches:
                debug_print(f"  - {name}: {solution_count} solutions")
    else:
        debug_print("WARNING: repo results CSV not found, cannot determine repos with solutions")
    
    if DEBUG:
        debug_print(f"Repositories with solutions from CSV: {sorted(repos_with_solutions)}")
    
    # Also look for solution checklist files directly to catch repos that may have
    # incomplete repo tasks but still have solutions to process
    solution_checklist_files = list(TASKS_DIR.glob('*_solution_checklist.md'))
    if solution_checklist_files:
        debug_print(f"Found {len(solution_checklist_files)} solution checklist files")
        for checklist_file in solution_checklist_files:
            # Extract repo name from solution checklist filename
            # Format: {repo_name}_solution_checklist.md or solutions_{repo_name}.md
            filename = checklist_file.stem
            if filename.endswith('_solution_checklist'):
                repo_name = filename.replace('_solution_checklist', '')
                repos_with_solutions.add(repo_name)
                if DEBUG:
                    debug_print(f"Added repository '{repo_name}' from solution checklist file")
            elif filename.startswith('solutions_'):
                repo_name = filename.replace('solutions_', '')
                repos_with_solutions.add(repo_name)
                if DEBUG:
                    debug_print(f"Added repository '{repo_name}' from solution checklist file")
    
    if DEBUG:
        debug_print(f"Final repositories with solutions to process: {sorted(repos_with_solutions)}")
    
    if len(repos_with_solutions) == 0:
        debug_print("WARNING: No repositories with solutions found")
        debug_print("Solution processing will be skipped")
    
    return repos_with_solutions


def process_solutions(
    repos_with_solutions: Set[str],
    final_incomplete_repos: List[Dict[str, Any]]
) -> Tuple[
    List[Dict[str, Any]],
    int,
    int,
    List[Any],
    List[Any],
    List[Any],
    List[Dict[str, Any]]
]:
    """
    Process all solution tasks with retry logic.
    
    This function will process solutions regardless of repository task completion status.
    
    Args:
        repos_with_solutions: Set of repository names with solutions
        final_incomplete_repos: List of repositories that still have incomplete tasks
        
    Returns:
        Tuple of (
            solution_details,
            successful_count,
            failed_count,
            incomplete_solutions,
            solution_checklist_files,
            skipped_solutions,
            final_failed_solutions
        )
    """
    if len(final_incomplete_repos) > 0:
        debug_print(
            f"WARNING: {len(final_incomplete_repos)} repositories still have "
            "incomplete tasks after retry"
        )
        if DEBUG:
            debug_print("Still incomplete repositories:")
            for repo in final_incomplete_repos:
                debug_print(f"  - {repo['repo_name']}: {len(repo['incomplete_tasks'])} incomplete tasks")
        debug_print(
            f"Will proceed to process solutions for {len(repos_with_solutions)} "
            "repositories with solutions (ignoring incomplete repo tasks)"
        )
    else:
        debug_print("All repositories completed successfully after retries")
    
    # Discover incomplete solutions (proceed regardless of repo task completion status)
    incomplete_solutions = solution_ops.discover_incomplete(
        repos_with_solutions, 
        ignore_repo_completion=True
    )
    
    # For statistics
    solution_checklist_files = list(TASKS_DIR.glob('*_solution_checklist.md'))
    skipped_solutions = []
    
    solution_details = []
    pending_solutions: List[Dict[str, Any]] = list(incomplete_solutions)
    processed_solution_keys: Set[Tuple[str, str]] = set()
    successful_solution_keys: Set[Tuple[str, str]] = set()
    final_failed_solutions: List[Dict[str, Any]] = []
    solution_attempt = 1
    
    while pending_solutions and solution_attempt <= MAX_SOLUTION_ATTEMPTS:
        debug_print(
            f"processing {len(pending_solutions)} solutions "
            f"(attempt {solution_attempt}/{MAX_SOLUTION_ATTEMPTS})"
        )
        
        next_pending: List[Dict[str, Any]] = []
        attempt_results: List[Dict[str, Any]] = []
        
        for solution in pending_solutions:
            solution_copy = dict(solution)
            solution_name = solution_copy['solution_name']
            checklist_path = solution_copy['checklist_path']
            parent_repo = solution_copy.get('parent_repo')
            display_name = (
                solution_copy.get('solution_display_name')
                or solution_name
            )
            solution_key = (parent_repo, solution_name)
            processed_solution_keys.add(solution_key)
            
            reset_required = bool(solution_copy.pop('needs_reset', False))
            extra_purge = {
                value for value in solution_copy.pop('purge_candidates', [])
                if isinstance(value, str) and value.strip()
            }

            identifier_values: Set[str] = {
                value.strip()
                for value in {
                    display_name,
                    solution_name
                }
                if isinstance(value, str) and value.strip()
            }
            if '_' in solution_name:
                suffix = solution_name.split('_', 1)[1]
                identifier_values.update({
                    suffix,
                    suffix.replace('_', ' '),
                    suffix.replace('_', '.')
                })
            if display_name:
                identifier_values.update({
                    display_name.replace('_', ' '),
                    display_name.replace('_', '.'),
                })
            identifier_values.update(extra_purge)
            solution_copy['identifier_values'] = list(identifier_values)

            if reset_required:
                solution_ops.reset_tasks(Path(checklist_path))
                purge_solution_results(parent_repo or '', identifier_values)
            
            result_detail = solution_ops.execute_task(
                solution_name,
                checklist_path
            )
            result_detail.update({
                'parent_repo': parent_repo,
                'solution_display_name': solution_copy.get('solution_display_name'),
                'attempt': solution_attempt
            })
            solution_details.append(result_detail)
            
            solution_copy['execution_status'] = result_detail['execution_status']
            attempt_results.append(solution_copy)
        
        verification_results = solution_ops.verify_tasks_completed(
            repo_filter=repos_with_solutions
        )
        verification_map: Dict[Path, Dict[str, Any]] = {}
        for entry in verification_results:
            checklist = entry.get('checklist_path')
            if not checklist:
                continue
            verification_map[Path(checklist).resolve()] = entry
        
        for result in attempt_results:
            solution_name = result.get('solution_name')
            parent_repo = result.get('parent_repo')
            solution_key = (parent_repo, solution_name)
            
            if result.get('execution_status') != 'SUCCESS':
                if solution_attempt < MAX_SOLUTION_ATTEMPTS:
                    retry_entry = {
                        key: value
                        for key, value in result.items()
                        if key not in {'execution_status', 'attempt'}
                    }
                    retry_entry['needs_reset'] = True
                    candidate_values = set(result.get('identifier_values', []))
                    if candidate_values:
                        retry_entry['purge_candidates'] = list(candidate_values)
                    next_pending.append(retry_entry)
                else:
                    failure_record = {
                        'parent_repo': parent_repo,
                        'solution_name': solution_name,
                        'solution_display_name': result.get('solution_display_name'),
                        'checklist_path': result.get('checklist_path'),
                        'reason': 'execution failure'
                    }
                    final_failed_solutions.append(failure_record)
                result.pop('identifier_values', None)
                continue
            
            checklist_value = result.get('checklist_path')
            checklist_real = Path(checklist_value).resolve() if checklist_value else None
            verification_issue = (
                verification_map.get(checklist_real)
                if checklist_real is not None
                else None
            )
            if verification_issue:
                reason_text = '; '.join(
                    verification_issue.get('incomplete_tasks', [])
                ) or 'solution checklist verification failed'
                debug_print(
                    (
                        "solution {repo}/{solution} failed verification: {reason}"
                    ).format(
                        repo=parent_repo,
                        solution=solution_name,
                        reason=reason_text
                    )
                )
                purge_identifiers: Set[str] = {
                    value
                    for value in {
                        solution_name,
                        result.get('solution_display_name'),
                        verification_issue.get('solution_display_name'),
                        verification_issue.get('solution_slug')
                    }
                    if isinstance(value, str) and value.strip()
                }
                if solution_attempt < MAX_SOLUTION_ATTEMPTS:
                    retry_entry = {
                        key: value
                        for key, value in result.items()
                        if key not in {'execution_status', 'attempt'}
                    }
                    retry_entry['needs_reset'] = True
                    candidate_values = set(result.get('identifier_values', []))
                    candidate_values.update(purge_identifiers)
                    if candidate_values:
                        retry_entry['purge_candidates'] = list(candidate_values)
                    next_pending.append(retry_entry)
                else:
                    failure_record = {
                        'parent_repo': parent_repo,
                        'solution_name': solution_name,
                        'solution_display_name': result.get('solution_display_name'),
                        'checklist_path': result.get('checklist_path'),
                        'reason': reason_text
                    }
                    final_failed_solutions.append(failure_record)
                result.pop('identifier_values', None)
                continue
            
            successful_solution_keys.add(solution_key)
            result.pop('identifier_values', None)
        
        pending_solutions = next_pending
        solution_attempt += 1
    
    solution_successful_count = len(successful_solution_keys)
    failed_solution_keys = processed_solution_keys - successful_solution_keys
    solution_failed_count = len(failed_solution_keys)
    
    if final_failed_solutions and DEBUG:
        debug_print("solutions that failed after retries:")
        for failure in final_failed_solutions:
            debug_print(
                f"  - {failure.get('parent_repo')}/{failure.get('solution_name')}: "
                f"{failure.get('reason', 'unknown reason')}"
            )
    
    debug_print(
        f"solution processing complete: processed={len(solution_details)} "
        f"successful={solution_successful_count} failed={solution_failed_count}"
    )
    
    return (
        solution_details,
        solution_successful_count,
        solution_failed_count,
        incomplete_solutions,
        solution_checklist_files,
        skipped_solutions,
        final_failed_solutions
    )


def generate_workflow_summary(
    append_mode: bool,
    start_time: datetime.datetime,
    total_repositories: int,
    incomplete_repos: List[Any],
    repository_details: List[Dict[str, Any]],
    successful_count: int,
    failed_count: int,
    solution_checklist_files: List[Any],
    incomplete_solutions: List[Any],
    solution_details: List[Dict[str, Any]],
    solution_successful_count: int,
    solution_failed_count: int,
    final_failed_solutions: List[Any],
    skipped_solutions: List[Any]
) -> Tuple[Dict[str, Any], str]:
    """
    Generate workflow summary and results.
    
    Returns:
        Tuple of (result dictionary, workflow status)
    """
    end_time = datetime.datetime.now(datetime.timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    # Determine workflow status
    total_failed = failed_count + solution_failed_count
    total_successful = successful_count + solution_successful_count
    
    if total_failed == 0:
        workflow_status = "SUCCESS"
    elif total_successful > 0:
        workflow_status = "PARTIAL_SUCCESS"
    else:
        workflow_status = "FAIL"
    
    processed_repo_count = len(set(r['repo_name'] for r in repository_details if 'repo_name' in r))
    processed_solution_count = len(set(
        (s.get('parent_repo'), s.get('solution_name'))
        for s in solution_details
        if s.get('parent_repo') and s.get('solution_name')
    ))
    
    result = {
        "append_mode": append_mode,
        "total_repositories": total_repositories,
        "incomplete_repositories": len(incomplete_repos),
        "processed_repositories": processed_repo_count,
        "successful_repositories": successful_count,
        "failed_repositories": failed_count,
        "repository_details": repository_details,
        "total_solutions": len(solution_checklist_files),
        "incomplete_solutions": len(incomplete_solutions),
        "processed_solutions": processed_solution_count,
        "successful_solutions": solution_successful_count,
        "failed_solutions": solution_failed_count,
        "solution_details": solution_details,
        "solution_retry_failures": final_failed_solutions,
        "skipped_solutions": skipped_solutions,
        "skipped_solutions_count": len(skipped_solutions),
        "workflow_status": workflow_status,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "status": "SUCCESS" if workflow_status != "FAIL" else "FAIL"
    }
    
    # Log final summary
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(f"\n{'='*80}\n")
        log.write("Workflow Completed\n")
        log.write(f"End Time: {end_time.isoformat()}\n")
        log.write(f"Duration: {duration:.2f} seconds\n")
        log.write(f"Workflow Status: {workflow_status}\n")
        log.write(f"Repositories: {successful_count} successful, {failed_count} failed\n")
        log.write(f"Solutions: {solution_successful_count} successful, {solution_failed_count} failed\n")
        log.write(f"{'='*80}\n")
    
    # Print summary
    if DEBUG:
        debug_print(f"Total repositories processed: {processed_repo_count}")
        debug_print(f"Successful: {successful_count}")
        debug_print(f"Failed: {failed_count}")
        debug_print(f"Total solutions processed: {processed_solution_count}")
        debug_print(f"Solutions successful: {solution_successful_count}")
        debug_print(f"Solutions failed: {solution_failed_count}")
        debug_print(f"Processing time: {duration:.2f} seconds")
    
    return result, workflow_status


def main():
    """Main orchestration workflow."""
    parser = argparse.ArgumentParser(
        description='Orchestrate repository workflow'
    )
    parser.add_argument(
        '--append',
        action='store_true',
        help='Append mode (preserve existing files)'
    )
    parser.add_argument(
        '--solutions-only',
        action='store_true',
        help='Skip repository processing and only execute solution processing'
    )
    parser.add_argument(
        '--repo-only',
        action='store_true',
        help='Skip solution processing and only execute repository processing'
    )
    args = parser.parse_args()

    append_mode = args.append
    solutions_only = args.solutions_only
    repo_only = args.repo_only

    # Validate arguments
    if solutions_only and repo_only:
        print("ERROR: Cannot specify both --solutions-only and --repo-only")
        return 1

    debug_print(f"START append={append_mode} solutions_only={solutions_only} repo_only={repo_only}")
    if solutions_only:
        debug_print("solutions_only mode: skipping repository processing")
    if repo_only:
        debug_print("repo_only mode: skipping solution processing")

    try:
        # Initialize workflow
        start_time = initialize_workflow(append_mode, solutions_only, repo_only)
        
        # Initialize result tracking
        repository_details = []
        successful_count = 0
        failed_count = 0
        total_repositories = 0
        incomplete_repos = []
        final_incomplete_repos = []
        
        # Process repositories (unless solutions_only mode)
        if not solutions_only:
            repository_details, successful_count, failed_count, total_repositories, final_incomplete_repos = \
                process_repositories(append_mode)
        else:
            debug_print("solutions_only mode: skipping repository verification")
        
        # Process solutions (unless repo_only mode)
        solution_details = []
        solution_successful_count = 0
        solution_failed_count = 0
        incomplete_solutions = []
        solution_checklist_files = []
        skipped_solutions = []
        final_failed_solutions: List[Dict[str, Any]] = []
        
        if not repo_only:
            repos_with_solutions = build_repos_with_solutions()
            
            solution_details, solution_successful_count, solution_failed_count, \
                incomplete_solutions, solution_checklist_files, skipped_solutions, \
                final_failed_solutions = \
                process_solutions(repos_with_solutions, final_incomplete_repos)
        else:
            debug_print("repo_only mode: skipping solution processing")
        
        # Generate summary and output
        result, workflow_status = generate_workflow_summary(
            append_mode,
            start_time,
            total_repositories,
            incomplete_repos,
            repository_details,
            successful_count,
            failed_count,
            solution_checklist_files,
            incomplete_solutions,
            solution_details,
            solution_successful_count,
            solution_failed_count,
            final_failed_solutions,
            skipped_solutions
        )
        
        with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        debug_print(
            f"EXIT status={workflow_status} "
            f"processed={len(repository_details)} "
            f"successful={successful_count} failed={failed_count}"
        )
        
        return 0 if workflow_status != "FAIL" else 1

    except Exception as e:
        debug_print(f"FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

        result = {
            "append_mode": append_mode,
            "workflow_status": "FAIL",
            "error_message": str(e),
            "status": "FAIL"
        }
        with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        return 1


if __name__ == '__main__':
    debug_print("script saved to: ./tools/orchestrate_repo_workflow.py")
    print("\nScript generated: ./tools/orchestrate_repo_workflow.py")
    print(
        'To execute: $env:DEBUG = "1"; '
        'python ./tools/orchestrate_repo_workflow.py'
    )
    print(
        'All command output will be logged to: '
        './orchestrate_repo_workflow.log'
    )

    # Execute the workflow
    sys.exit(main())
