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
7. Processing solution checklists

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
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

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


def debug_print(message: str):
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        print(f"[debug][orchestrate-repo-workflow] {message}")


def clean_directories():
    """Remove files from results, tasks, output, and temp-script dirs."""
    debug_print("cleaned results, tasks, output, temp-script directories")

    for directory in [RESULTS_DIR, TASKS_DIR, OUTPUT_DIR, TEMP_SCRIPT_DIR]:
        if directory.exists():
            for item in directory.iterdir():
                if item.is_file():
                    item.unlink()
                    debug_print(f"  removed file: {item}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    debug_print(f"  removed directory: {item}")


def ensure_solution_results_csv():
    """Create solution_result.csv with expected header when missing."""
    csv_path = RESULTS_DIR / 'solution_result.csv'

    if csv_path.exists():
        return

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(csv_path, 'w', encoding='utf-8', newline='') as handle:
        handle.write('repo,solution,task name,status\n')

    debug_print("initialized solution_result.csv in results directory")


def ensure_repo_results_csv():
    """Create repo_result.csv with expected header when missing."""
    csv_path = RESULTS_DIR / 'repo_result.csv'

    if csv_path.exists():
        return

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(csv_path, 'w', encoding='utf-8', newline='') as handle:
        handle.write('repo,task name,status\n')

    debug_print("initialized repo_result.csv in results directory")


def run_copilot_command(command: str) -> Tuple[int, str, str]:
    """
    Execute a copilot command using subprocess.
    Logs all output to orchestrate_repo_workflow.log

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    debug_print(f"executing: {command}")

    # Log command to file
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(f"\n{'='*80}\n")
        log.write(f"[{timestamp}] Executing command:\n")
        log.write(f"{command}\n")
        log.write(f"{'='*80}\n\n")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    # Log output to file
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(f"Exit Code: {result.returncode}\n\n")

        if result.stdout:
            log.write("STDOUT:\n")
            log.write(result.stdout)
            log.write("\n\n")

        if result.stderr:
            log.write("STDERR:\n")
            log.write(result.stderr)
            log.write("\n\n")

    return result.returncode, result.stdout, result.stderr


def verify_repo_checklist_format() -> bool:
    """
    Verify repository checklist format inline.
    Implements logic from verify-repo-checklist-format.prompt.md

    IMPORTANT - Format Verification Logic:
    - Check each checklist file for required sections:
      * Must have: # Task Checklist: {repo_name} header
      * Must have: ## Repo Tasks section
      * Must have EITHER: ## Task Variables OR ## Repo Variables Available
        - Note: ## Task Variables is created by execute-repo-task
            when the first task runs
    - Newly generated checklists only have ## Repo Variables Available
    - This is NORMAL and should NOT fail verification
    - Only fail if BOTH sections are missing

    Returns:
        True if all checklists pass format verification, False otherwise
    """
    debug_print(
        "executing inline verification from "
        "verify-repo-checklist-format.prompt.md"
    )

    # Find all repo checklist files
    checklist_files = list(TASKS_DIR.glob('*_repo_checklist.md'))
    checklist_files = [
        f for f in checklist_files
        if f.name != 'all_repository_checklist.md'
    ]

    if not checklist_files:
        debug_print("ERROR: No repository checklist files found")
        return False

    debug_print(f"found {len(checklist_files)} repository checklist files")

    all_passed = True
    issues = []

    for checklist_path in checklist_files:
        repo_name = checklist_path.stem.replace('_repo_checklist', '')
        debug_print(f"verifying format for: {repo_name}")

        with open(checklist_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check basic structure
        if not lines:
            issues.append(f"{repo_name}: File is empty")
            all_passed = False
            continue

        # Verify header
        if not lines[0].strip().startswith('# Task Checklist:'):
            issues.append(f"{repo_name}: Missing or incorrect header")
            all_passed = False

        # Look for required sections
        has_repo_tasks = any('## Repo Tasks' in line for line in lines)
        has_task_variables = any('## Task Variables' in line for line in lines)
        has_repo_variables = any(
            '## Repo Variables Available' in line
            for line in lines
        )

        if not has_repo_tasks:
            issues.append(f"{repo_name}: Missing '## Repo Tasks' section")
            all_passed = False

        # Task Variables section is created when first task executes
        # It's OK to be missing in newly generated checklists
        # But we need at least the Repo Variables Available section
        if not has_task_variables and not has_repo_variables:
            issues.append(
                f"{repo_name}: Missing both '## Task Variables' and "
                "'## Repo Variables Available' sections"
            )
            all_passed = False

    # Save results
    result = {
        "total_checklists": len(checklist_files),
        "passed": len(checklist_files) - len(issues),
        "failed": len(issues),
        "issues": issues,
        "overall_status": "PASS" if all_passed else "FAIL",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_DIR / 'verify-repo-checklist-format.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Save markdown report
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(
        RESULTS_DIR / 'repo-checklist-format-verification.md', 'w'
    ) as f:
        f.write("# Repository Checklist Format Verification\n\n")
        f.write(f"Generated: {result['timestamp']}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Total Checklists: {result['total_checklists']}\n")
        f.write(f"- Passed: {result['passed']}\n")
        f.write(f"- Failed: {result['failed']}\n")
        f.write(f"- Overall Status: {result['overall_status']}\n\n")

        if issues:
            f.write("## Issues Found\n\n")
            for issue in issues:
                f.write(f"- {issue}\n")

    if all_passed:
        debug_print(
            "verify-repo-checklist-format completed successfully - "
            "all checklists properly formatted"
        )
    else:
        debug_print(
            "ERROR: verify-repo-checklist-format failed - "
            "checklists have format issues"
        )

    return all_passed


def verify_repo_tasks_completed() -> List[Dict[str, any]]:
    """
    Verify repository tasks completion inline.
    Implements logic from verify-repo-tasks-completed.prompt.md

    Returns:
        List of repositories with incomplete tasks. Each dict contains:
        - repo_name: str
        - checklist_path: str
        - incomplete_tasks: List[str]
        - total_tasks: int
        - completed_tasks: int
        Empty list means all repositories are complete.
    """
    debug_print(
        "executing inline verification from "
        "verify-repo-tasks-completed.prompt.md"
    )

    # Find all repo checklist files
    checklist_files = list(TASKS_DIR.glob('*_repo_checklist.md'))
    checklist_files = [
        f for f in checklist_files
        if f.name != 'all_repository_checklist.md'
    ]

    if not checklist_files:
        debug_print("ERROR: No repository checklist files found")
        return False

    debug_print(f"found {len(checklist_files)} repository checklist files")

    all_passed = True
    repo_results = {}
    incomplete_repos = []

    for checklist_path in checklist_files:
        repo_name = checklist_path.stem.replace('_repo_checklist', '')
        debug_print(f"verifying completion for: {repo_name}")

        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find Repo Tasks section
        repo_tasks_match = re.search(
            r'## Repo Tasks.*?\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if not repo_tasks_match:
            repo_results[repo_name] = {
                "all_completed": False,
                "incomplete_tasks": ["Could not find Repo Tasks section"]
            }
            all_passed = False
            incomplete_repos.append({
                "repo_name": repo_name,
                "checklist_path": str(checklist_path),
                "incomplete_tasks": ["Could not find Repo Tasks section"],
                "total_tasks": 0,
                "completed_tasks": 0
            })
            continue

        repo_tasks_section = repo_tasks_match.group(1)

        # Count incomplete tasks
        incomplete_tasks = re.findall(r'- \[ \] (.+)', repo_tasks_section)
        completed_tasks = re.findall(r'- \[x\] (.+)', repo_tasks_section)

        repo_results[repo_name] = {
            "total_tasks": len(incomplete_tasks) + len(completed_tasks),
            "completed_tasks": len(completed_tasks),
            "incomplete_tasks": incomplete_tasks,
            "all_completed": len(incomplete_tasks) == 0
        }

        if incomplete_tasks:
            all_passed = False
            debug_print(
                f"  {repo_name} has {len(incomplete_tasks)} incomplete tasks"
            )
            incomplete_repos.append({
                "repo_name": repo_name,
                "checklist_path": str(checklist_path),
                "incomplete_tasks": incomplete_tasks,
                "total_tasks": len(incomplete_tasks) + len(completed_tasks),
                "completed_tasks": len(completed_tasks)
            })
        else:
            debug_print(f"  {repo_name} all tasks completed")

    # Verify repo_result.csv has solution count for each repository
    repo_results_csv_path = RESULTS_DIR / 'repo_result.csv'
    if repo_results_csv_path.exists():
        debug_print("verifying repo_result.csv for solution counts")

        with open(repo_results_csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()

        for repo_name in repo_results.keys():
            # Look for task-find-solutions row for this repository
            # Format can be either:
            #   timestamp|repo_name|task-find-solutions|N solutions|SUCCESS|✓
            #   timestamp|repo_name|task-find-solutions|SUCCESS|✓
            # Note: CSV may use either | or , as delimiter
            pattern = rf'{re.escape(repo_name)}[|,]task-find-solutions[|,]'
            match = re.search(pattern, csv_content)

            if not match:
                debug_print(
                    (
                        "  ERROR: {repo} missing task-find-solutions entry in "
                        "repo_result.csv"
                    ).format(repo=repo_name)
                )
                repo_results[repo_name]["all_completed"] = False
                if "incomplete_tasks" not in repo_results[repo_name]:
                    repo_results[repo_name]["incomplete_tasks"] = []
                repo_results[repo_name]["incomplete_tasks"].append(
                    "Missing task-find-solutions entry in repo_result.csv"
                )
                all_passed = False

                # Add to incomplete_repos if not already there
                if not any(r['repo_name'] == repo_name for r in incomplete_repos):
                    incomplete_repos.append({
                        "repo_name": repo_name,
                        "checklist_path": str(TASKS_DIR / f"{repo_name}_repo_checklist.md"),
                        "incomplete_tasks": [
                            "Missing task-find-solutions entry in repo_result.csv"
                        ],
                        "total_tasks": repo_results[repo_name].get("total_tasks", 0),
                        "completed_tasks": repo_results[repo_name].get("completed_tasks", 0)
                    })
            else:
                # Extract solution count if present
                # Pattern: timestamp|repo_name|task-find-solutions|N solutions|...
                count_pattern = rf'{re.escape(repo_name)}[|,]task-find-solutions[|,](\d+) solutions?[|,]'
                count_match = re.search(count_pattern, csv_content)

                if count_match:
                    solution_count = int(count_match.group(1))
                    debug_print(
                        (
                            "  {repo} has {count} solutions in repo_result.csv"
                        ).format(repo=repo_name, count=solution_count)
                    )
                    # Store solution count for later verification
                    repo_results[repo_name]["expected_solutions"] = solution_count
                else:
                    # Entry exists but no solution count specified
                    debug_print(
                        f"  {repo_name} has task-find-solutions entry "
                        "(solution count not specified)"
                    )
    else:
        debug_print(
            "ERROR: repo_result.csv not found - marking all repositories as incomplete"
        )
    # Mark all repositories as incomplete if repo_result.csv doesn't exist
        for repo_name in repo_results.keys():
            repo_results[repo_name]["all_completed"] = False
            if "incomplete_tasks" not in repo_results[repo_name]:
                repo_results[repo_name]["incomplete_tasks"] = []
            repo_results[repo_name]["incomplete_tasks"].append(
                "repo_result.csv file not found"
            )
            all_passed = False

            # Add to incomplete_repos if not already there
            if not any(r['repo_name'] == repo_name for r in incomplete_repos):
                incomplete_repos.append({
                    "repo_name": repo_name,
                    "checklist_path": str(TASKS_DIR / f"{repo_name}_repo_checklist.md"),
                    "incomplete_tasks": ["repo_result.csv file not found"],
                    "total_tasks": repo_results[repo_name].get("total_tasks", 0),
                    "completed_tasks": repo_results[repo_name].get("completed_tasks", 0)
                })

    # Save results
    result = {
        "total_repositories": len(checklist_files),
        "repositories_passing": sum(
            1 for r in repo_results.values() if r['all_completed']
        ),
        "repositories_failing": sum(
            1 for r in repo_results.values() if not r['all_completed']
        ),
        "repository_details": repo_results,
        "overall_status": "PASS" if all_passed else "FAIL",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    with open(OUTPUT_DIR / 'verify-repo-tasks-completed.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Save markdown report
    with open(RESULTS_DIR / 'repo-tasks-verification.md', 'w') as f:
        f.write("# Repository Tasks Verification\n\n")
        f.write(f"Generated: {result['timestamp']}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Total Repositories: {result['total_repositories']}\n")
        f.write(f"- Passing: {result['repositories_passing']}\n")
        f.write(f"- Failing: {result['repositories_failing']}\n")
        f.write(f"- Overall Status: {result['overall_status']}\n\n")

        for repo_name, details in repo_results.items():
            f.write(f"### {repo_name}\n\n")
            f.write(f"- Total Tasks: {details['total_tasks']}\n")
            f.write(f"- Completed: {details['completed_tasks']}\n")
            status = 'PASS' if details['all_completed'] else 'FAIL'
            f.write(f"- Status: {status}\n")

            if details['incomplete_tasks']:
                f.write("- Incomplete Tasks:\n")
                for task in details['incomplete_tasks']:
                    f.write(f"  - {task}\n")
            f.write("\n")

    if all_passed:
        debug_print(
            "verify-repo-tasks-completed completed successfully - "
            "all repositories have completed tasks"
        )
    else:
        debug_print(
            "ERROR: verify-repo-tasks-completed failed - "
            "some repositories have incomplete tasks or invalid variables"
        )

    return incomplete_repos


def generate_repo_task_checklists(input_file: str, append: bool) -> bool:
    """
    Generate repository task checklists from a repositories input file.

    Args:
        input_file: Path to the file containing repository URLs
        append: If True, preserve existing checklists; if False, regenerate all

    Returns:
        True if generation succeeded, False otherwise
    """
    debug_print(
        f"generating repository checklists from {input_file} "
        f"(append={append})"
    )

    cmd = (
        f'copilot --prompt "/generate-repo-task-checklists '
        f'input=\\"{input_file}\\" '
        f'append={str(append).lower()}" --allow-all-tools --allow-all-paths'
    )
    exit_code, stdout, stderr = run_copilot_command(cmd)

    if exit_code != 0:
        debug_print(
            f"ERROR: generate-repo-task-checklists failed with "
            f"exit code {exit_code}"
        )
        return False

    debug_print("generate-repo-task-checklists completed successfully")
    return True


def reset_repo_tasks(checklist_path: str, incomplete_tasks: List[str]) -> bool:
    """
    Reset incomplete tasks in a repository checklist from [x] to [ ].
    Also removes corresponding rows from repo_result.csv.

    Args:
        checklist_path: Path to the repository checklist file
        incomplete_tasks: List of task descriptions that are incomplete

    Returns:
        True if tasks were reset successfully, False otherwise
    """
    debug_print(f"resetting tasks in {checklist_path}")

    try:
        # Extract repo name from checklist path
        checklist_file = Path(checklist_path)
        repo_name = checklist_file.stem.replace('_repo_checklist', '')

        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find Repo Tasks section
        repo_tasks_match = re.search(
            r'(## Repo Tasks.*?\n)(.*?)((?=\n##|\Z))',
            content,
            re.DOTALL
        )

        if not repo_tasks_match:
            debug_print(f"ERROR: Could not find Repo Tasks section in {checklist_path}")
            return False

        header = repo_tasks_match.group(1)
        tasks_section = repo_tasks_match.group(2)
        remainder = repo_tasks_match.group(3)

        # Reset all completed tasks to incomplete
        # Change - [x] to - [ ]
        modified_tasks = re.sub(r'- \[x\]', '- [ ]', tasks_section)

        # Reconstruct the content
        before_section = content[:repo_tasks_match.start()]
        after_section = content[repo_tasks_match.end():]
        new_content = before_section + header + modified_tasks + remainder + after_section

        # Write back to file
        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        debug_print(f"successfully reset tasks in {checklist_path}")

        # Remove rows from repo_result.csv for this repository
        repo_results_csv = RESULTS_DIR / 'repo_result.csv'
        if repo_results_csv.exists():
            debug_print(
                f"removing {repo_name} entries from repo_result.csv"
            )

            with open(repo_results_csv, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Keep header and lines that don't match this repo
            filtered_lines = []
            removed_count = 0

            for line in lines:
                # Check if this line is for the current repository
                # CSV format: timestamp|repo_name|task|status|symbol
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 2:
                        line_repo_name = parts[1].strip()
                        if line_repo_name == repo_name:
                            removed_count += 1
                            debug_print(f"  removed: {line.strip()}")
                            continue

                filtered_lines.append(line)

            # Write back filtered content
            with open(repo_results_csv, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)

            debug_print(
                f"removed {removed_count} entries for {repo_name} from repo_result.csv"
            )

        return True

    except Exception as e:
        debug_print(f"ERROR: Failed to reset tasks in {checklist_path}: {str(e)}")
        return False


def reset_solution_tasks(checklist_path: Path) -> bool:
    """Reset all completed solution tasks to unchecked state."""
    try:
        with open(checklist_path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        section_match = re.search(
            r'(### Tasks.*?)(?=\n###|\n##|\Z)',
            content,
            re.DOTALL
        )

        if not section_match:
            section_match = re.search(
                r'(## Solution Tasks.*?)(?=\n##|\Z)',
                content,
                re.DOTALL
            )

        if not section_match:
            debug_print(
                (
                    "WARNING: could not find solution tasks section in {path}"
                ).format(path=checklist_path)
            )
            return False

        modified_section = re.sub(r'- \[x\]', '- [ ]', section_match.group(0))
        content = (
            content[:section_match.start()]
            + modified_section
            + content[section_match.end():]
        )

        with open(checklist_path, 'w', encoding='utf-8') as handle:
            handle.write(content)

        debug_print(f"solution tasks reset in {checklist_path}")
        return True

    except Exception as exc:  # noqa: BLE001
        debug_print(
            (
                "ERROR: failed to reset solution tasks in {path}: {error}"
            ).format(path=checklist_path, error=exc)
        )
        return False


def purge_solution_results(
    csv_path: Path,
    repo_name: str,
    solution_name: str
) -> int:
    """Remove rows for a repo/solution pair from solution_result.csv."""
    if not csv_path.exists():
        debug_print("solution_result.csv not found - nothing to purge")
        return 0

    removed = 0
    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames or [
                'repo',
                'solution',
                'task name',
                'status'
            ]

        filtered_rows = []
        for row in rows:
            repo_value = (row.get('repo') or row.get('Repository') or '').strip()
            solution_value = (
                row.get('solution') or row.get('Solution') or ''
            ).strip()

            if repo_value == repo_name and solution_value == solution_name:
                removed += 1
                continue

            filtered_rows.append(row)

        if removed:
            with open(csv_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filtered_rows)

        debug_print(
            (
                "purged {count} rows for repo '{repo}' solution '{solution}' "
                "from solution_result.csv"
            ).format(
                count=removed,
                repo=repo_name,
                solution=solution_name
            )
        )

    except Exception as exc:  # noqa: BLE001
        debug_print(
            (
                "ERROR: failed to purge solution_result.csv for repo '{repo}' "
                "solution '{solution}': {error}"
            ).format(
                repo=repo_name,
                solution=solution_name,
                error=exc
            )
        )
        return 0

    return removed


def validate_solution_results(
    solutions: List[Dict[str, Any]],
    csv_path: Path
) -> List[Dict[str, str]]:
    """Ensure each processed solution has at least one entry in CSV."""
    if not solutions:
        return []

    if not csv_path.exists():
        debug_print(
            "solution_result.csv missing - all processed solutions will "
            "be treated as failures"
        )
        failures = []
        for solution in solutions:
            failures.append(
                {
                    'solution_name': solution.get('solution_name'),
                    'solution_display_name': solution.get('solution_display_name'),
                    'parent_repo': solution.get('parent_repo'),
                    'checklist_path': solution.get('checklist_path'),
                    'reason': 'solution_result.csv missing'
                }
            )
        return failures

    entry_counts = defaultdict(int)

    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                repo_value = (row.get('repo') or row.get('Repository') or '').strip()
                solution_value = (
                    row.get('solution') or row.get('Solution') or ''
                ).strip()

                if repo_value and solution_value:
                    entry_counts[(repo_value, solution_value)] += 1

    except Exception as exc:  # noqa: BLE001
        debug_print(
            f"ERROR: unable to read solution_result.csv: {exc}"
        )
        return [
            {
                'solution_name': item.get('solution_name'),
                'solution_display_name': item.get('solution_display_name'),
                'parent_repo': item.get('parent_repo'),
                'checklist_path': item.get('checklist_path'),
                'reason': 'solution_result.csv unreadable'
            }
            for item in solutions
        ]

    failures = []
    for solution in solutions:
        repo_name = solution.get('parent_repo')
        display_name = solution.get('solution_display_name')
        slug_name = solution.get('solution_name')

        effective_name = display_name or slug_name

        if not repo_name or not effective_name:
            failures.append(
                {
                    'solution_name': slug_name,
                    'solution_display_name': display_name,
                    'parent_repo': repo_name,
                    'checklist_path': solution.get('checklist_path'),
                    'reason': 'missing repo or solution name for validation'
                }
            )
            continue

        if entry_counts[(repo_name, effective_name)] == 0:
            failures.append(
                {
                    'solution_name': slug_name,
                    'solution_display_name': display_name,
                    'parent_repo': repo_name,
                    'checklist_path': solution.get('checklist_path'),
                    'reason': 'solution_result.csv missing entry'
                }
            )

    return failures


def execute_repo_task(repo_name: str, checklist_path: str, clone_dir: str = "./clone_repos") -> Dict[str, any]:

    """
    Execute tasks for a single repository checklist.

    Args:
        repo_name: Name of the repository
        checklist_path: Path to the repository checklist file
        clone_dir: Directory where repositories will be cloned (default: "./clone_repos")

    Returns:
        Dictionary with execution details:
        - repo_name: str
        - checklist_path: str
        - execution_status: "SUCCESS" | "FAIL"
        - exit_code: int
        - error_message: str | None
    """
    debug_print(f"processing repository: {repo_name}")

    # Execute repository tasks
    cmd = (
        f'copilot --prompt "/execute-repo-task '
        f'repo_checklist=\\"{checklist_path}\\" '
        f'clone=\\"{clone_dir}\\"" --allow-all-tools --allow-all-paths'
    )
    exit_code, stdout, stderr = run_copilot_command(cmd)

    if exit_code == 0:
        debug_print(f"execute-repo-task completed for {repo_name}")
        return {
            "repo_name": repo_name,
            "checklist_path": checklist_path,
            "execution_status": "SUCCESS",
            "exit_code": exit_code,
            "error_message": None
        }
    else:
        debug_print(
            f"ERROR: execute-repo-task failed for {repo_name} "
            f"with exit code {exit_code}"
        )
        debug_print("continuing to next repository despite failure")
        return {
            "repo_name": repo_name,
            "checklist_path": checklist_path,
            "execution_status": "FAIL",
            "exit_code": exit_code,
            "error_message": (
                f"execute-repo-task failed with exit code {exit_code}"
            )
        }


def execute_solution_task(solution_name: str, solution_checklist_path: str) -> Dict[str, any]:
    """
    Execute tasks for a single solution checklist.

    Args:
        solution_name: Name of the solution (without _solution_checklist.md suffix)
        solution_checklist_path: Path to the solution checklist file

    Returns:
        Dictionary with execution details:
        - solution_name: str
        - checklist_path: str
        - execution_status: "SUCCESS" | "FAIL"
        - exit_code: int
        - error_message: str | None
    """
    debug_print(f"processing solution: {solution_name}")

    # Execute solution tasks
    cmd = (
        f'copilot --prompt "/execute-solution-task '
        f'solution_checklist=\\"{solution_checklist_path}\\"" --allow-all-tools --allow-all-paths'
    )
    debug_print(f"executing: {cmd}")
    exit_code, stdout, stderr = run_copilot_command(cmd)

    if exit_code == 0:
        debug_print(f"execute-solution-task completed for {solution_name}")
        return {
            "solution_name": solution_name,
            "checklist_path": solution_checklist_path,
            "execution_status": "SUCCESS",
            "exit_code": exit_code,
            "error_message": None
        }
    else:
        debug_print(
            f"ERROR: execute-solution-task failed for {solution_name} "
            f"with exit code {exit_code}"
        )
        debug_print("continuing to next solution despite failure")
        return {
            "solution_name": solution_name,
            "checklist_path": solution_checklist_path,
            "execution_status": "FAIL",
            "exit_code": exit_code,
            "error_message": (
                f"execute-solution-task failed with exit code {exit_code}"
            )
        }


def discover_incomplete_repositories() -> List[Dict[str, str]]:
    """
    Find all repository checklists with incomplete tasks.

    Returns:
        List of dictionaries with repo_name and checklist_path
    """
    debug_print("discovering repository checklists")

    checklist_files = list(TASKS_DIR.glob('*_repo_checklist.md'))
    checklist_files = [
        f for f in checklist_files
        if f.name != 'all_repository_checklist.md'
    ]

    debug_print(f"found {len(checklist_files)} repository checklist files")

    incomplete_repos = []

    for checklist_path in checklist_files:
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find Repo Tasks section using regex
        repo_tasks_match = re.search(
            r'## Repo Tasks.*?\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if repo_tasks_match:
            repo_tasks_section = repo_tasks_match.group(1)

            # Check for incomplete tasks
            if re.search(r'- \[ \]', repo_tasks_section):
                repo_name = checklist_path.stem.replace('_repo_checklist', '')
                incomplete_repos.append({
                    'repo_name': repo_name,
                    'checklist_path': str(checklist_path)
                })

    debug_print(
        f"found {len(incomplete_repos)} repositories with incomplete tasks"
    )

    if DEBUG and incomplete_repos:
        debug_print("repositories to process:")
        for repo in incomplete_repos:
            debug_print(f"  - {repo['checklist_path']}")

    return incomplete_repos


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
        help='Skip repository processing and go straight to solution processing'
    )
    args = parser.parse_args()

    append_mode = args.append
    solutions_only = args.solutions_only

    debug_print(f"START append={append_mode} solutions_only={solutions_only}")
    debug_print(f"using append_mode: {append_mode}")
    if solutions_only:
        debug_print("solutions_only mode: skipping repository processing")

    start_time = datetime.datetime.now(datetime.timezone.utc)

    # Initialize log file
    with open(LOG_FILE, 'w', encoding='utf-8') as log:
        log.write(f"Orchestrate Repository Workflow Log\n")
        log.write(f"Started: {start_time.isoformat()}\n")
        log.write(f"Append Mode: {append_mode}\n")
        log.write(f"Solutions Only: {solutions_only}\n")
        log.write(f"{'='*80}\n\n")

    # Initialize result tracking
    repository_details = []
    successful_count = 0
    failed_count = 0
    total_repositories = 0
    incomplete_repos = []

    try:
        # Step 2: Clean directories if append=false and not solutions_only
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

        # Skip repository processing if solutions_only mode
        if not solutions_only:
            # Step 3: Generate repository checklists
            if not generate_repo_task_checklists('repositories_small.txt', append_mode):
                result = {
                    "append_mode": append_mode,
                    "workflow_status": "FAIL",
                    "error_message": "Failed to generate repository task checklists",
                    "status": "FAIL"
                }
                with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
                    json.dump(result, f, indent=2)
                return 1

            # Step 3a: Verify repository checklist format
            if not verify_repo_checklist_format():
                result = {
                    "append_mode": append_mode,
                    "workflow_status": "FAIL",
                    "error_message": "Repository checklist format verification failed",
                    "status": "FAIL"
                }
                with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
                    json.dump(result, f, indent=2)
                return 1

            # Step 4-6: Discover incomplete repositories
            incomplete_repos = discover_incomplete_repositories()

            # Count total repositories
            all_checklist_files = list(TASKS_DIR.glob('*_repo_checklist.md'))
            total_repositories = len([
                f for f in all_checklist_files
                if f.name != 'all_repository_checklist.md'
            ])

            if not incomplete_repos:
                debug_print("All repositories already complete")
                result = {
                    "append_mode": append_mode,
                    "total_repositories": total_repositories,
                    "incomplete_repositories": 0,
                    "processed_repositories": 0,
                    "successful_repositories": 0,
                    "failed_repositories": 0,
                    "repository_details": [],
                    "workflow_status": "SUCCESS",
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                    "duration_seconds": (
                        datetime.datetime.now(datetime.timezone.utc) - start_time
                    ).total_seconds(),
                    "status": "SUCCESS"
                }
                with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
                    json.dump(result, f, indent=2)

                debug_print("EXIT status=SUCCESS processed=0 successful=0 failed=0")
                # Don't return, continue to solution processing

            # Step 7: Process repositories with retries
            processed_repo_names: Set[str] = set()
            successful_repo_names: Set[str] = set()
            final_incomplete_map: Dict[str, Dict[str, Any]] = {}

            pending_repos: List[Dict[str, Any]] = list(incomplete_repos)
            repo_attempt = 1

            while pending_repos and repo_attempt <= MAX_REPO_ATTEMPTS:
                debug_print(
                    (
                        "processing {count} repositories "
                        "(attempt {attempt}/{max_attempts})"
                    ).format(
                        count=len(pending_repos),
                        attempt=repo_attempt,
                        max_attempts=MAX_REPO_ATTEMPTS
                    )
                )

                next_pending: List[Dict[str, Any]] = []

                for repo in pending_repos:
                    repo_name = repo['repo_name']
                    checklist_path = repo['checklist_path']
                    processed_repo_names.add(repo_name)

                    result_detail = execute_repo_task(
                        repo_name,
                        checklist_path,
                        "./clone_repos"
                    )
                    result_detail['attempt'] = repo_attempt
                    repository_details.append(result_detail)

                    if result_detail['execution_status'] == 'SUCCESS':
                        successful_repo_names.add(repo_name)

                verification_results = verify_repo_tasks_completed()
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
                            reset_repo_tasks(
                                retry_entry['checklist_path'],
                                retry_entry.get('incomplete_tasks', [])
                            )
                            next_pending.append(retry_entry)
                        else:
                            final_incomplete_map[repo_name] = incomplete_map[repo_name]
                            successful_repo_names.discard(repo_name)
                    else:
                        successful_repo_names.add(repo_name)

                pending_repos = next_pending
                repo_attempt += 1

            final_incomplete_repos = list(final_incomplete_map.values())
            final_incomplete_names = set(final_incomplete_map.keys())

            if processed_repo_names:
                successful_count = len(
                    [
                        name for name in successful_repo_names
                        if name not in final_incomplete_names
                    ]
                )
                failed_repo_names = (
                    (processed_repo_names - successful_repo_names)
                    | final_incomplete_names
                )
                failed_count = len(failed_repo_names)
            else:
                successful_count = 0
                failed_count = 0
            processed_repo_count = len(processed_repo_names)
        else:
            # solutions_only mode: skip verification, assume repos complete
            debug_print("solutions_only mode: skipping repository verification")
            final_incomplete_repos = []
            processed_repo_count = 0

        # Build set of repository names that have solution checklists to process.
        # We process solutions if task-find-solutions succeeded (entry in repo_result.csv)
        # even when some repo tasks still need retries.
        repos_with_solutions = set()
        repo_results_csv_path = RESULTS_DIR / 'repo_result.csv'

        if repo_results_csv_path.exists():
            with open(repo_results_csv_path, 'r', encoding='utf-8') as handle:
                csv_content = handle.read()

            if DEBUG:
                debug_print(
                    "Searching for task-find-solutions entries in repo_result.csv"
                )
                debug_print(
                    f"CSV content length: {len(csv_content)} bytes"
                )

            pattern_all = r'[^|,]+[|,]([^|,]+)[|,]task-find-solutions[|,]'
            all_matches = re.findall(pattern_all, csv_content)

            if DEBUG:
                debug_print(
                    f"Found {len(all_matches)} task-find-solutions entries total"
                )

            for name in all_matches:
                repo_name = name.strip()
                repos_with_solutions.add(repo_name)
                if DEBUG:
                    debug_print(
                        (
                            "Repository '{repo}' has task-find-solutions entry"
                        ).format(repo=repo_name)
                    )

            pattern_with_count = (
                r'[^|,]+[|,]([^|,]+)[|,]task-find-solutions[|,](\d+) solutions?[|,]'
            )
            count_matches = re.findall(pattern_with_count, csv_content)

            if DEBUG and count_matches:
                debug_print("Repositories with solution counts:")
                for name, solution_count in count_matches:
                    debug_print(f"  - {name}: {solution_count} solutions")
        else:
            debug_print(
                "WARNING: repo_result.csv not found, cannot determine repos with solutions"
            )

        if DEBUG:
            debug_print(f"Repositories with solutions to process: {sorted(repos_with_solutions)}")

        if len(repos_with_solutions) == 0:
            debug_print("WARNING: No repositories with task-find-solutions entries found")
            debug_print("Solution processing will be skipped")

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
                f"Will only process solutions for {len(repos_with_solutions)} "
                "repositories with solutions"
            )
        else:
            debug_print("All repositories completed successfully after retries")

        # Step 7b: Process Solution Checklists
        solution_details = []
        solution_successful_count = 0
        solution_failed_count = 0

        # 7b.a: Discover solution checklists
        solution_checklist_files = list(TASKS_DIR.glob('*_solution_checklist.md'))
        debug_print(f"found {len(solution_checklist_files)} solution checklist files")

        # 7b.b: Filter for incomplete solutions
        incomplete_solutions = []
        skipped_solutions = []
        for checklist_path in solution_checklist_files:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()

            solution_path_match = re.search(
                r'Solution Path:\s*`([^`]+)`',
                content
            )
            solution_display_name = None
            if solution_path_match:
                solution_path_value = solution_path_match.group(1)
                solution_display_name = Path(solution_path_value).stem
            else:
                alternate_match = re.search(
                    r'Solution Path:\s*[\'"]([^\'"]+)[\'"]',
                    content
                )
                if alternate_match:
                    solution_display_name = Path(
                        alternate_match.group(1)
                    ).stem

            # Extract repository name from solution checklist filename
            # Format: {org}_{repo}_{solution}_solution_checklist.md
            solution_filename = checklist_path.stem.replace(
                '_solution_checklist', ''
            )

            # Determine the repository name this solution belongs to
            # Check if any repo with solutions has a name that is
            # a prefix of the solution name
            belongs_to_repo_with_solutions = False
            parent_repo = None
            for repo_name in repos_with_solutions:
                # Check if solution name starts with repo name
                if solution_filename.startswith(repo_name):
                    belongs_to_repo_with_solutions = True
                    parent_repo = repo_name
                    break

            # Debug: show why solution is being skipped
            if DEBUG and not belongs_to_repo_with_solutions:
                debug_print(
                    f"Solution '{solution_filename}' - checking against "
                    f"repos with solutions: {sorted(repos_with_solutions)}"
                )

            # Skip solutions from repositories that don't have solutions
            if not belongs_to_repo_with_solutions:
                debug_print(
                    f"Skipping solution {solution_filename} - "
                    "parent repository not completed"
                )
                continue

            # Find Solution Tasks section using regex (support legacy formats)
            solution_tasks_section = ''
            solution_tasks_match = re.search(
                r'## Solution Tasks.*?\n(.*?)(?=\n##|\Z)',
                content,
                re.DOTALL
            )

            if solution_tasks_match:
                solution_tasks_section = solution_tasks_match.group(1)
            else:
                # Some checklists use "### Tasks" instead
                alternative_tasks_match = re.search(
                    r'### Tasks.*?\n(.*?)(?=\n##|\n###|\Z)',
                    content,
                    re.DOTALL
                )
                if alternative_tasks_match:
                    solution_tasks_section = alternative_tasks_match.group(1)

            mandatory_incomplete: List[str] = []
            if solution_tasks_section:
                mandatory_matches = re.findall(
                    r'- \[(?P<status>[ xX])\]\s+\[MANDATORY[^\]]*\]\s+(.+)',
                    solution_tasks_section
                )
                for status, description in mandatory_matches:
                    if status.lower() != 'x':
                        mandatory_incomplete.append(description.strip())
            else:
                if DEBUG:
                    debug_print(
                        (
                            "  WARNING: Solution checklist "
                            f"'{checklist_path.name}' missing tasks section"
                        )
                    )

            solution_variables_match = re.search(
                r'### Solution Variables.*?\n(.*?)(?=\n###|\n##|\Z)',
                content,
                re.DOTALL
            )
            variables_section = (
                solution_variables_match.group(1).strip()
                if solution_variables_match
                else ''
            )
            variables_set = bool(variables_section)

            solution_name = checklist_path.stem.replace(
                '_solution_checklist', ''
            )

            if not variables_set:
                skipped_solutions.append({
                    'solution_name': solution_name,
                    'checklist_path': str(checklist_path),
                    'parent_repo': parent_repo,
                    'solution_display_name': solution_display_name,
                    'reason': 'Solution Variables section missing or empty'
                })
                if DEBUG:
                    debug_print(
                        (
                            "  Skipping solution '{name}' - "
                            "solution variables not set"
                        ).format(name=solution_name)
                    )
                continue

            if mandatory_incomplete:
                incomplete_solutions.append({
                    'solution_name': solution_name,
                    'checklist_path': str(checklist_path),
                    'parent_repo': parent_repo,
                    'solution_display_name': solution_display_name,
                    'mandatory_incomplete': mandatory_incomplete
                })
                if DEBUG:
                    debug_print(
                        (
                            "  Added solution '{name}' (missing mandatory "
                            "tasks: {count})"
                        ).format(
                            name=solution_name,
                            count=len(mandatory_incomplete)
                        )
                    )
            else:
                if DEBUG:
                    debug_print(
                        (
                            "  All mandatory tasks complete for solution "
                            "'{name}' - skipping"
                        ).format(name=solution_name)
                    )

        debug_print(
            (
                "found {count} solution checklists to process from "
                "repositories with solutions"
            ).format(count=len(incomplete_solutions))
        )

        if skipped_solutions and DEBUG:
            debug_print("skipping solution checklists due to unset variables:")
            for skipped in skipped_solutions:
                debug_print(
                    f"  - {skipped['checklist_path']} ({skipped['reason']})"
                )

        # 7b.c: Print incomplete solution list
        if DEBUG and incomplete_solutions:
            debug_print("solution checklists to process:")
            for solution in incomplete_solutions:
                debug_print(f"  - {solution['checklist_path']}")
        elif not DEBUG and incomplete_solutions:
            processing_count = len(incomplete_solutions)
            print(
                (
                    "Processing {count} solution checklists with "
                    "incomplete tasks"
                ).format(count=processing_count)
            )

        pending_solutions: List[Dict[str, Any]] = list(incomplete_solutions)
        processed_solution_keys: Set[Tuple[str, str]] = set()
        successful_solution_keys: Set[Tuple[str, str]] = set()
        final_failed_solutions: List[Dict[str, Any]] = []
        solution_attempt = 1

        while pending_solutions and solution_attempt <= MAX_SOLUTION_ATTEMPTS:
            debug_print(
                (
                    "processing {count} solutions (attempt {attempt}/{max_attempts})"
                ).format(
                    count=len(pending_solutions),
                    attempt=solution_attempt,
                    max_attempts=MAX_SOLUTION_ATTEMPTS
                )
            )

            next_pending: List[Dict[str, Any]] = []
            attempt_results: List[Dict[str, Any]] = []
            csv_path = RESULTS_DIR / 'solution_result.csv'

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

                reset_solution_tasks(Path(checklist_path))
                purge_solution_results(csv_path, parent_repo or '', display_name)

                result_detail = execute_solution_task(
                    solution_name,
                    checklist_path
                )
                result_detail.update(
                    {
                        'parent_repo': parent_repo,
                        'solution_display_name': solution_copy.get('solution_display_name'),
                        'attempt': solution_attempt
                    }
                )
                solution_details.append(result_detail)

                solution_copy['execution_status'] = result_detail['execution_status']
                attempt_results.append(solution_copy)

            successful_this_attempt = [
                item for item in attempt_results
                if item.get('execution_status') == 'SUCCESS'
            ]

            validation_failures = validate_solution_results(
                successful_this_attempt,
                csv_path
            )
            failure_map = {
                (item.get('parent_repo'), item.get('solution_name')): item
                for item in validation_failures
            }

            for result in attempt_results:
                solution_name = result.get('solution_name')
                parent_repo = result.get('parent_repo')
                solution_key = (parent_repo, solution_name)

                if result.get('execution_status') != 'SUCCESS':
                    if solution_attempt < MAX_SOLUTION_ATTEMPTS:
                        next_pending.append(
                            {
                                key: value
                                for key, value in result.items()
                                if key != 'execution_status'
                            }
                        )
                    else:
                        final_failed_solutions.append(
                            {
                                **result,
                                'reason': 'execution failure'
                            }
                        )
                    continue

                if solution_key in failure_map:
                    if solution_attempt < MAX_SOLUTION_ATTEMPTS:
                        next_pending.append(
                            {
                                key: value
                                for key, value in result.items()
                                if key != 'execution_status'
                            }
                        )
                    else:
                        failure_info = failure_map[solution_key]
                        final_failed_solutions.append(
                            {
                                **result,
                                'reason': failure_info.get('reason')
                            }
                        )
                    continue

                successful_solution_keys.add(solution_key)

            pending_solutions = next_pending
            solution_attempt += 1

        solution_successful_count = len(successful_solution_keys)
        failed_solution_keys = processed_solution_keys - successful_solution_keys
        solution_failed_count = len(failed_solution_keys)
        processed_solution_count = len(processed_solution_keys)

        if final_failed_solutions and DEBUG:
            debug_print("solutions that failed after retries:")
            for failure in final_failed_solutions:
                debug_print(
                    (
                        "  - {repo}/{name}: {reason}"
                    ).format(
                        repo=failure.get('parent_repo'),
                        name=failure.get('solution_name'),
                        reason=failure.get('reason', 'unknown reason')
                    )
                )

        debug_print(
            (
                "solution processing complete: processed={processed} "
                "successful={successful} failed={failed}"
            ).format(
                processed=len(solution_details),
                successful=solution_successful_count,
                failed=solution_failed_count
            )
        )

        # Step 8-10: Generate summary and output
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

        with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
            json.dump(result, f, indent=2)

        # Log final summary to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(f"\n{'='*80}\n")
            log.write("Workflow Completed\n")
            log.write(f"End Time: {end_time.isoformat()}\n")
            log.write(f"Duration: {duration:.2f} seconds\n")
            log.write(f"Workflow Status: {workflow_status}\n")
            log.write(
                (
                    "Repositories: {success} successful, {failed} failed\n"
                ).format(
                    success=successful_count,
                    failed=failed_count
                )
            )
            log.write(
                (
                    "Solutions: {success} successful, {failed} failed\n"
                ).format(
                    success=solution_successful_count,
                    failed=solution_failed_count
                )
            )
            log.write(f"{'='*80}\n")

        # Print summary
        if DEBUG:
            debug_print(
                (
                    "Total repositories processed: {count}"
                ).format(count=processed_repo_count)
            )
            debug_print(f"Successful: {successful_count}")
            debug_print(f"Failed: {failed_count}")
            debug_print(
                (
                    "Total solutions processed: {count}"
                ).format(count=processed_solution_count)
            )
            debug_print(f"Solutions successful: {solution_successful_count}")
            debug_print(f"Solutions failed: {solution_failed_count}")
            debug_print(f"Processing time: {duration:.2f} seconds")

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
        with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
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
