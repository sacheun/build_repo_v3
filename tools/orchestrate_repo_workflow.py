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


def debug_print(message: str):
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        print(f"[debug][orchestrate-repo-workflow] {message}")


def clean_directories():
    """Remove all files in results, tasks, and output directories."""
    debug_print("cleaned results, tasks, output directories")
    
    for directory in [RESULTS_DIR, TASKS_DIR, OUTPUT_DIR]:
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
    
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    debug_print(f"executing: {command}")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    
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


def verify_repo_tasks_completed() -> bool:
    """
    Verify repository tasks completion inline.
    Implements logic from verify-repo-tasks-completed.prompt.md
    
    Returns:
        True if all repositories have completed tasks, False otherwise
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
        else:
            debug_print(f"  {repo_name} all tasks completed")
    
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
    
    return all_passed


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
    args = parser.parse_args()
    
    append_mode = args.append
    
    debug_print(f"START append={append_mode}")
    debug_print(f"using append_mode: {append_mode}")
    
    start_time = datetime.datetime.now(datetime.timezone.utc)
    
    # Initialize result tracking
    repository_details = []
    successful_count = 0
    failed_count = 0
    
    try:
        # Step 2: Clean directories if append=false
        if not append_mode:
            clean_directories()
        else:
            debug_print("preserving existing files (append=true)")
        
        # Ensure directories exist
        for directory in [TASKS_DIR, OUTPUT_DIR, RESULTS_DIR, TOOLS_DIR]:
            directory.mkdir(exist_ok=True)
        
        # Step 3: Generate repository checklists
        cmd = (
            'copilot --prompt "/generate-repo-task-checklists '
            f'input=\\"repositories_small.txt\\" '
            f'append={str(append_mode).lower()}" --allow-all-tools'
        )
        exit_code, stdout, stderr = run_copilot_command(cmd)
        
        if exit_code != 0:
            debug_print(
                f"ERROR: generate-repo-task-checklists failed with "
                f"exit code {exit_code}"
            )
            result = {
                "append_mode": append_mode,
                "workflow_status": "FAIL",
                "error_message": (
                    f"generate-repo-task-checklists failed with "
                    f"exit code {exit_code}"
                ),
                "status": "FAIL"
            }
            with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
                json.dump(result, f, indent=2)
            return 1
        
        debug_print("generate-repo-task-checklists completed successfully")
        
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
            return 0
        
        # Step 7: Process each repository sequentially
        for repo in incomplete_repos:
            repo_name = repo['repo_name']
            checklist_path = repo['checklist_path']
            
            debug_print(f"processing repository: {repo_name}")
            
            # Execute repository tasks
            cmd = (
                f'copilot --prompt "/execute-repo-task '
                f'repo_checklist=\\"{checklist_path}\\" '
                f'clone=\\"./clone_repos\\"" --allow-all-tools'
            )
            exit_code, stdout, stderr = run_copilot_command(cmd)
            
            if exit_code == 0:
                debug_print(f"execute-repo-task completed for {repo_name}")
                successful_count += 1
                repository_details.append({
                    "repo_name": repo_name,
                    "checklist_path": checklist_path,
                    "execution_status": "SUCCESS",
                    "exit_code": exit_code,
                    "error_message": None
                })
            else:
                debug_print(
                    f"ERROR: execute-repo-task failed for {repo_name} "
                    f"with exit code {exit_code}"
                )
                debug_print("continuing to next repository despite failure")
                failed_count += 1
                repository_details.append({
                    "repo_name": repo_name,
                    "checklist_path": checklist_path,
                    "execution_status": "FAIL",
                    "exit_code": exit_code,
                    "error_message": (
                        f"execute-repo-task failed with exit code {exit_code}"
                    )
                })
            
            # Update master checklist
            cmd = (
                f'copilot --prompt "/task-update-all-repo-checklist '
                f'repo_name=\\"{repo_name}\\"" --allow-all-tools'
            )
            debug_print(f"updating master checklist for {repo_name}")
            exit_code, stdout, stderr = run_copilot_command(cmd)
            
            if exit_code == 0:
                debug_print(f"master checklist updated for {repo_name}")
            else:
                debug_print(
                    f"WARNING: failed to update master checklist for {repo_name}"
                )
        
        # Step 7a: Verify repository tasks completed
        if not verify_repo_tasks_completed():
            debug_print("WARNING: verify-repo-tasks-completed reported issues")
        
        # Step 8-10: Generate summary and output
        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Determine workflow status
        if failed_count == 0:
            workflow_status = "SUCCESS"
        elif successful_count > 0:
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
            "workflow_status": workflow_status,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "status": "SUCCESS" if workflow_status != "FAIL" else "FAIL"
        }
        
        with open(OUTPUT_DIR / 'orchestrate-repo-workflow.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        # Print summary
        if DEBUG:
            debug_print(f"Total repositories processed: {len(repository_details)}")
            debug_print(f"Successful: {successful_count}")
            debug_print(f"Failed: {failed_count}")
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
    
    # Execute the workflow
    sys.exit(main())
