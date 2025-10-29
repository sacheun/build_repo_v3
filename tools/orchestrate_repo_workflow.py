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
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Global configuration
DEBUG = os.environ.get('DEBUG', '0') == '1'
TASKS_DIR = Path('./tasks')
OUTPUT_DIR = Path('./output')
RESULTS_DIR = Path('./results')
TOOLS_DIR = Path('./tools')
CLONE_DIR = Path('./clone_repos')
TEMP_SCRIPT_DIR = Path('./temp-script')
LOG_FILE = Path('./orchestrate_repo_workflow.log')


def debug_print(message: str):
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        print(f"[debug][orchestrate-repo-workflow] {message}")


def clean_directories():
    """Remove all files in results, tasks, output, and temp-script directories."""
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
    - Note: ## Task Variables is created by execute-repo-task when first task runs
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
    
    # Verify repo-results.csv has solution count for each repository
    repo_results_csv_path = RESULTS_DIR / 'repo-results.csv'
    if repo_results_csv_path.exists():
        debug_print("verifying repo-results.csv for solution counts")
        
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
                    f"  ERROR: {repo_name} missing task-find-solutions entry in repo-results.csv"
                )
                repo_results[repo_name]["all_completed"] = False
                if "incomplete_tasks" not in repo_results[repo_name]:
                    repo_results[repo_name]["incomplete_tasks"] = []
                repo_results[repo_name]["incomplete_tasks"].append(
                    "Missing task-find-solutions entry in repo-results.csv"
                )
                all_passed = False
                
                # Add to incomplete_repos if not already there
                if not any(r['repo_name'] == repo_name for r in incomplete_repos):
                    incomplete_repos.append({
                        "repo_name": repo_name,
                        "checklist_path": str(TASKS_DIR / f"{repo_name}_repo_checklist.md"),
                        "incomplete_tasks": ["Missing task-find-solutions entry in repo-results.csv"],
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
                        f"  {repo_name} has {solution_count} solutions "
                        "in repo-results.csv"
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
        debug_print("ERROR: repo-results.csv not found - marking all repositories as incomplete")
        # Mark all repositories as incomplete if repo-results.csv doesn't exist
        for repo_name in repo_results.keys():
            repo_results[repo_name]["all_completed"] = False
            if "incomplete_tasks" not in repo_results[repo_name]:
                repo_results[repo_name]["incomplete_tasks"] = []
            repo_results[repo_name]["incomplete_tasks"].append(
                "repo-results.csv file not found"
            )
            all_passed = False
            
            # Add to incomplete_repos if not already there
            if not any(r['repo_name'] == repo_name for r in incomplete_repos):
                incomplete_repos.append({
                    "repo_name": repo_name,
                    "checklist_path": str(TASKS_DIR / f"{repo_name}_repo_checklist.md"),
                    "incomplete_tasks": ["repo-results.csv file not found"],
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
        f'append={str(append).lower()}" --allow-all-tools'
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
    Also removes corresponding rows from repo-results.csv.
    
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
        
        # Remove rows from repo-results.csv for this repository
        repo_results_csv = RESULTS_DIR / 'repo-results.csv'
        if repo_results_csv.exists():
            debug_print(f"removing {repo_name} entries from repo-results.csv")
            
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
            
            debug_print(f"removed {removed_count} entries for {repo_name} from repo-results.csv")
        
        return True
        
    except Exception as e:
        debug_print(f"ERROR: Failed to reset tasks in {checklist_path}: {str(e)}")
        return False


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
        f'clone=\\"{clone_dir}\\"" --allow-all-tools'
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
        f'solution_checklist=\\"{solution_checklist_path}\\"" --allow-all-tools'
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
            
            # Step 7: Process each repository sequentially
            for repo in incomplete_repos:
                repo_name = repo['repo_name']
                checklist_path = repo['checklist_path']
                
                # Execute repository tasks
                result_detail = execute_repo_task(repo_name, checklist_path, "./clone_repos")
                repository_details.append(result_detail)
                
                # Update counters based on execution status
                if result_detail['execution_status'] == 'SUCCESS':
                    successful_count += 1
                else:
                    failed_count += 1
                
                # Update master checklist
#                cmd = (
#                    f'copilot --prompt "/task-update-all-repo-checklist '
#                    f'repo_name=\\"{repo_name}\\"" --allow-all-tools'
#                )
#                debug_print(f"updating master checklist for {repo_name}")
#                exit_code, stdout, stderr = run_copilot_command(cmd)
                
#                if exit_code == 0:
#                    debug_print(f"master checklist updated for {repo_name}")
#                else:
#                    debug_print(
#                        f"WARNING: failed to update master checklist for {repo_name}"
#                    )

            # Step 7a: Verify repository tasks completed
            incomplete_from_verification = verify_repo_tasks_completed()
            if len(incomplete_from_verification) > 0:
                debug_print(
                    f"ERROR: verify-repo-tasks-completed found {len(incomplete_from_verification)} "
                    "repositories with incomplete tasks or invalid variables"
                )
                if DEBUG:
                    debug_print("Incomplete repositories from verification:")
                    for repo in incomplete_from_verification:
                        debug_print(f"  - {repo['repo_name']}: {len(repo['incomplete_tasks'])} incomplete tasks")
                
                # Step 7a.1: Retry incomplete repositories
                debug_print(f"Retrying {len(incomplete_from_verification)} incomplete repositories")
                
                retry_successful_count = 0
                retry_failed_count = 0
                
                for repo_info in incomplete_from_verification:
                    repo_name = repo_info['repo_name']
                    checklist_path = repo_info['checklist_path']
                    incomplete_tasks = repo_info['incomplete_tasks']
                    
                    debug_print(f"retrying repository: {repo_name}")
                    
                    # Reset tasks from [x] to [ ]
                    if not reset_repo_tasks(checklist_path, incomplete_tasks):
                        debug_print(f"ERROR: Failed to reset tasks for {repo_name}, skipping retry")
                        retry_failed_count += 1
                        continue
                    
                    # Re-execute repository tasks
                    result_detail = execute_repo_task(repo_name, checklist_path, "./clone_repos")
                    
                    # Update repository_details (append retry result)
                    repository_details.append({
                        **result_detail,
                        "retry": True
                    })
                    
                    # Update counters based on execution status
                    if result_detail['execution_status'] == 'SUCCESS':
                        retry_successful_count += 1
                        successful_count += 1
                    else:
                        retry_failed_count += 1
                        failed_count += 1
                
                debug_print(
                    f"retry complete: successful={retry_successful_count} "
                    f"failed={retry_failed_count}"
                )
        
            # Step 7a.2: Verify repository tasks completed again after retries
            debug_print("Re-verifying repository tasks completion after retries")
            final_incomplete_repos = verify_repo_tasks_completed()
        else:
            # solutions_only mode: skip verification, assume repos complete
            debug_print("solutions_only mode: skipping repository verification")
            final_incomplete_repos = []
        
        # Build set of repository names that have solution checklists to process
        # A repository should process solutions if it has completed task-find-solutions
        # (i.e., has solutions logged in repo-results.csv), regardless of whether
        # all repo tasks are complete
        repos_with_solutions = set()
        repo_results_csv_path = RESULTS_DIR / 'repo-results.csv'
        
        if repo_results_csv_path.exists():
            with open(repo_results_csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            if DEBUG:
                debug_print("Searching for task-find-solutions entries in repo-results.csv")
                debug_print(f"CSV content length: {len(csv_content)} bytes")
            
            # Find all repositories that have task-find-solutions entry
            # CSV Format: timestamp,repo_name,task,status,symbol
            # Examples:
            #   2025-10-29T16:35:25Z,sync_calling_concore-conversation,task-find-solutions,13 solutions,SUCCESS,✓
            #   2025-10-29T16:22:03Z,ic3_spool_cosine-dep-spool,task-find-solutions,SUCCESS,✓
            #   2025-10-29T16:26:49Z|people_spool_usertokenmanagement|task-find-solutions|5 solutions|SUCCESS|✓
            # Support both | and , as separators
            import re
            
            # Match ANY entry with task-find-solutions, extract repo name
            # Pattern: timestamp (sep) repo_name (sep) task-find-solutions (sep) ...
            pattern_all = r'[^|,]+[|,]([^|,]+)[|,]task-find-solutions[|,]'
            all_matches = re.findall(pattern_all, csv_content)
            
            if DEBUG:
                debug_print(f"Found {len(all_matches)} task-find-solutions entries total")
            
            for repo_name in all_matches:
                repo_name = repo_name.strip()
                repos_with_solutions.add(repo_name)
                if DEBUG:
                    debug_print(f"Repository '{repo_name}' has task-find-solutions entry")
            
            # Also try to extract solution counts where available for logging
            pattern_with_count = r'[^|,]+[|,]([^|,]+)[|,]task-find-solutions[|,](\d+) solutions?[|,]'
            count_matches = re.findall(pattern_with_count, csv_content)
            
            if DEBUG and count_matches:
                debug_print(f"Repositories with solution counts:")
                for repo_name, solution_count in count_matches:
                    debug_print(f"  - {repo_name}: {solution_count} solutions")
        else:
            debug_print("WARNING: repo-results.csv not found, cannot determine repos with solutions")
        
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
        for checklist_path in solution_checklist_files:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract repository name from solution checklist filename
            # Format: {org}_{repo}_{solution}_solution_checklist.md
            solution_filename = checklist_path.stem.replace('_solution_checklist', '')
            
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

            has_incomplete_tasks = False
            if solution_tasks_section:
                has_incomplete_tasks = re.search(r'- \[ \]', solution_tasks_section) is not None
            else:
                if DEBUG:
                    debug_print(
                        f"  WARNING: Solution checklist '{checklist_path.name}' "
                        "missing tasks section"
                    )

            # Always add solutions from repos with solutions
            solution_name = checklist_path.stem.replace('_solution_checklist', '')
            incomplete_solutions.append({
                'solution_name': solution_name,
                'checklist_path': str(checklist_path),
                'parent_repo': parent_repo,
                'has_incomplete_tasks': has_incomplete_tasks
            })

            if DEBUG:
                status = "incomplete" if has_incomplete_tasks else "complete"
                debug_print(f"  Added solution '{solution_name}' ({status})")
        
        debug_print(
            f"found {len(incomplete_solutions)} solution checklists to process "
            f"from repositories with solutions"
        )
        
        # 7b.c: Print incomplete solution list
        if DEBUG and incomplete_solutions:
            debug_print("solution checklists to process:")
            for solution in incomplete_solutions:
                debug_print(f"  - {solution['checklist_path']}")
        elif not DEBUG and incomplete_solutions:
            print(f"Processing {len(incomplete_solutions)} solution checklists with incomplete tasks")
        
        # 7b.d: Process each solution checklist sequentially
        for solution in incomplete_solutions:
            solution_name = solution['solution_name']
            solution_checklist_path = solution['checklist_path']
            
            # Execute solution tasks
            result_detail = execute_solution_task(solution_name, solution_checklist_path)
            solution_details.append(result_detail)
            
            # Update counters based on execution status
            if result_detail['execution_status'] == 'SUCCESS':
                solution_successful_count += 1
            else:
                solution_failed_count += 1
        
        # 7b.e: Log solution processing summary
        debug_print(
            f"solution processing complete: "
            f"processed={len(solution_details)} "
            f"successful={solution_successful_count} "
            f"failed={solution_failed_count}"
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
            "processed_repositories": len(repository_details),
            "successful_repositories": successful_count,
            "failed_repositories": failed_count,
            "repository_details": repository_details,
            "total_solutions": len(solution_checklist_files),
            "incomplete_solutions": len(incomplete_solutions),
            "processed_solutions": len(solution_details),
            "successful_solutions": solution_successful_count,
            "failed_solutions": solution_failed_count,
            "solution_details": solution_details,
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
            log.write(f"Workflow Completed\n")
            log.write(f"End Time: {end_time.isoformat()}\n")
            log.write(f"Duration: {duration:.2f} seconds\n")
            log.write(f"Workflow Status: {workflow_status}\n")
            log.write(f"Repositories: {successful_count} successful, {failed_count} failed\n")
            log.write(f"Solutions: {solution_successful_count} successful, {solution_failed_count} failed\n")
            log.write(f"{'='*80}\n")
        
        # Print summary
        if DEBUG:
            debug_print(f"Total repositories processed: {len(repository_details)}")
            debug_print(f"Successful: {successful_count}")
            debug_print(f"Failed: {failed_count}")
            debug_print(f"Total solutions processed: {len(solution_details)}")
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
    print('To execute: $env:DEBUG = "1"; python ./tools/orchestrate_repo_workflow.py')
    print('All command output will be logged to: ./orchestrate_repo_workflow.log')
    
    # Execute the workflow
    sys.exit(main())
