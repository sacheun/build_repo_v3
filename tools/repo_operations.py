#!/usr/bin/env python3
"""
Repository Operations Module

This module provides functions for repository-level operations including:
- Generating repository task checklists
- Verifying checklist formats
- Verifying task completion
- Resetting tasks
- Executing repository tasks
- Discovering incomplete repositories

Usage:
    from repo_operations import RepoOperations
    
    repo_ops = RepoOperations(
        tasks_dir='./tasks',
        output_dir='./output', 
        results_dir='./results',
        copilot_executor=copilot,
        debug=True
    )
    
    # Generate checklists
    success = repo_ops.generate_task_checklists('repositories.txt', append=False)
    
    # Execute repository tasks
    result = repo_ops.execute_task('my_repo', './tasks/my_repo_checklist.md')
"""

import datetime
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any

class RepoOperations:
    """Handles all repository-level operations."""
    
    def __init__(
        self,
        tasks_dir: Path,
        output_dir: Path,
        results_dir: Path,
        copilot_executor,
        debug: bool = False
    ):
        """
        Initialize repository operations.
        
        Args:
            tasks_dir: Directory containing task checklists
            output_dir: Directory for output JSON files
            results_dir: Directory for result reports
            copilot_executor: CopilotExecutor instance for running commands
            debug: Enable debug output
        """
        self.tasks_dir = tasks_dir
        self.output_dir = output_dir
        self.results_dir = results_dir
        self.copilot = copilot_executor
        self.debug = debug
    
    def _debug_print(self, message: str):
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"[debug][repo-operations] {message}")
    
    def verify_checklist_format(self) -> bool:
        """
        Verify repository checklist format.
        Implements logic from verify-repo-checklist-format.prompt.md
        
        Returns:
            True if all checklists pass format verification, False otherwise
        """
        self._debug_print(
            "executing inline verification from "
            "verify-repo-checklist-format.prompt.md"
        )
        
        # Find all repo checklist files
        checklist_files = list(self.tasks_dir.glob('*_repo_checklist.md'))
        checklist_files = [
            f for f in checklist_files 
            if f.name != 'all_repository_checklist.md'
        ]
        
        if not checklist_files:
            self._debug_print("ERROR: No repository checklist files found")
            return False
        
        self._debug_print(f"found {len(checklist_files)} repository checklist files")
        
        all_passed = True
        issues = []
        
        for checklist_path in checklist_files:
            repo_name = checklist_path.stem.replace('_repo_checklist', '')
            self._debug_print(f"verifying format for: {repo_name}")
            
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
        
        self.output_dir.mkdir(exist_ok=True)
        with open(self.output_dir / 'verify-repo-checklist-format.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        # Save markdown report
        self.results_dir.mkdir(exist_ok=True)
        with open(
            self.results_dir / 'repo-checklist-format-verification.md', 'w'
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
            self._debug_print(
                "verify-repo-checklist-format completed successfully - "
                "all checklists properly formatted"
            )
        else:
            self._debug_print(
                "ERROR: verify-repo-checklist-format failed - "
                "checklists have format issues"
            )
        
        return all_passed
    
    def verify_tasks_completed(self, skip_csv_check: bool = False) -> List[Dict[str, Any]]:
        """
        Verify repository tasks completion by checking MANDATORY tasks only.
        
        Args:
            skip_csv_check: If True, skip verification of repo-results.csv entries
        
        Returns:
            List of repositories with incomplete MANDATORY tasks. Empty list means all complete.
        """
        self._debug_print("verifying MANDATORY tasks completion in repo checklists")
        
        # Find all repo checklist files
        checklist_files = list(self.tasks_dir.glob('*_repo_checklist.md'))
        checklist_files = [
            f for f in checklist_files 
            if f.name != 'all_repository_checklist.md'
        ]
        
        if not checklist_files:
            self._debug_print("ERROR: No repository checklist files found")
            return []
        
        self._debug_print(f"found {len(checklist_files)} repository checklist files")
        
        incomplete_repos = []
        
        for checklist_path in checklist_files:
            repo_name = checklist_path.stem.replace('_repo_checklist', '')
            self._debug_print(f"verifying completion for: {repo_name}")
            
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Repo Tasks section
            repo_tasks_match = re.search(
                r'## Repo Tasks.*?\n(.*?)(?=\n##|\Z)', 
                content, 
                re.DOTALL
            )
            
            if not repo_tasks_match:
                self._debug_print(f"  ERROR: Could not find Repo Tasks section")
                incomplete_repos.append({
                    "repo_name": repo_name,
                    "checklist_path": str(checklist_path),
                    "incomplete_tasks": ["Could not find Repo Tasks section"],
                    "total_tasks": 0,
                    "completed_tasks": 0
                })
                continue
            
            repo_tasks_section = repo_tasks_match.group(1)
            
            # Find incomplete MANDATORY tasks only
            incomplete_mandatory = re.findall(
                r'- \[ \] \[MANDATORY[^\]]*\].*?@(\S+)',
                repo_tasks_section
            )
            
            # Find completed MANDATORY tasks
            completed_mandatory = re.findall(
                r'- \[x\] \[MANDATORY[^\]]*\].*?@(\S+)',
                repo_tasks_section
            )
            
            total_mandatory = len(incomplete_mandatory) + len(completed_mandatory)
            
            if incomplete_mandatory:
                self._debug_print(
                    f"  {repo_name} has {len(incomplete_mandatory)}/{total_mandatory} "
                    f"incomplete MANDATORY tasks: {incomplete_mandatory}"
                )
                incomplete_repos.append({
                    "repo_name": repo_name,
                    "checklist_path": str(checklist_path),
                    "incomplete_tasks": incomplete_mandatory,
                    "total_tasks": total_mandatory,
                    "completed_tasks": len(completed_mandatory)
                })
            else:
                self._debug_print(
                    f"  {repo_name} all {total_mandatory} MANDATORY tasks completed"
                )
        
        # Verify repo-results.csv has entries for each completed MANDATORY task
        if not skip_csv_check:
            repo_results_csv_path = self.results_dir / 'repo-results.csv'
            if repo_results_csv_path.exists():
                self._debug_print("verifying repo-results.csv has entries for completed MANDATORY tasks")
            
            with open(repo_results_csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            # Re-check all checklists to verify CSV entries
            for checklist_path in checklist_files:
                repo_name = checklist_path.stem.replace('_repo_checklist', '')
                
                with open(checklist_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                repo_tasks_match = re.search(
                    r'## Repo Tasks.*?\n(.*?)(?=\n##|\Z)', 
                    content, 
                    re.DOTALL
                )
                
                if not repo_tasks_match:
                    continue
                
                repo_tasks_section = repo_tasks_match.group(1)
                
                # Find all completed MANDATORY tasks with their task names
                completed_mandatory_tasks = re.findall(
                    r'- \[x\] \[MANDATORY[^\]]*\].*?@([\w\-]+)',
                    repo_tasks_section
                )
                
                # Check if each completed MANDATORY task has a CSV entry
                missing_csv_entries = []
                for task_name in completed_mandatory_tasks:
                    # Look for pattern: repo_name, task_name in CSV
                    pattern = rf'{re.escape(repo_name)}\s*[|,]\s*{re.escape(task_name)}'
                    if not re.search(pattern, csv_content):
                        missing_csv_entries.append(task_name)
                        self._debug_print(
                            f"  ERROR: {repo_name} completed task '{task_name}' "
                            "missing from repo-results.csv"
                        )
                
                # If there are missing CSV entries, mark repo as incomplete
                if missing_csv_entries:
                    # Check if already in incomplete_repos
                    existing = next(
                        (r for r in incomplete_repos if r['repo_name'] == repo_name),
                        None
                    )
                    
                    if existing:
                        # Add to existing incomplete tasks
                        for task in missing_csv_entries:
                            existing['incomplete_tasks'].append(
                                f"CSV entry missing for {task}"
                            )
                    else:
                        # Add new entry
                        incomplete_repos.append({
                            "repo_name": repo_name,
                            "checklist_path": str(checklist_path),
                            "incomplete_tasks": [
                                f"CSV entry missing for {task}" for task in missing_csv_entries
                            ],
                            "total_tasks": len(completed_mandatory_tasks),
                            "completed_tasks": len(completed_mandatory_tasks) - len(missing_csv_entries)
                        })
            else:
                self._debug_print("WARNING: repo-results.csv not found - cannot verify CSV entries")
        else:
            self._debug_print("skipping repo-results.csv verification (skip_csv_check=True)")
        
        # Summary
        if incomplete_repos:
            self._debug_print(
                f"found {len(incomplete_repos)} repositories with incomplete MANDATORY tasks"
            )
        else:
            self._debug_print("all repositories have completed MANDATORY tasks")
        
        return incomplete_repos
    
    def generate_task_checklists(self, input_file: str, append: bool) -> bool:
        """
        Generate repository task checklists from a repositories input file.
        
        Args:
            input_file: Path to the file containing repository URLs
            append: If True, preserve existing checklists; if False, regenerate all
        
        Returns:
            True if generation succeeded, False otherwise
        """
        self._debug_print(
            f"generating repository checklists from {input_file} "
            f"(append={append})"
        )
        
        exit_code, stdout, stderr = self.copilot.execute_prompt(
            'generate-repo-task-checklists',
            {'input': input_file, 'append': str(append).lower()}
        )
        
        if exit_code != 0:
            self._debug_print(
                f"ERROR: generate-repo-task-checklists failed with "
                f"exit code {exit_code}"
            )
            return False
        
        self._debug_print("generate-repo-task-checklists completed successfully")
        return True
    
    def reset_tasks(self, checklist_path: str, incomplete_tasks: List[str]) -> bool:
        """
        Reset incomplete tasks in a repository checklist from [x] to [ ].
        
        Args:
            checklist_path: Path to the repository checklist file
            incomplete_tasks: List of task descriptions that are incomplete
        
        Returns:
            True if tasks were reset successfully, False otherwise
        """
        self._debug_print(f"resetting tasks in {checklist_path}")
        
        try:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Repo Tasks section
            repo_tasks_match = re.search(
                r'(## Repo Tasks.*?\n)(.*?)((?=\n##|\Z))', 
                content, 
                re.DOTALL
            )
            
            if not repo_tasks_match:
                self._debug_print(f"ERROR: Could not find Repo Tasks section in {checklist_path}")
                return False
            
            header = repo_tasks_match.group(1)
            tasks_section = repo_tasks_match.group(2)
            remainder = repo_tasks_match.group(3)
            
            # Reset all completed tasks to incomplete
            modified_tasks = re.sub(r'- \[x\]', '- [ ]', tasks_section)
            
            # Reconstruct the content
            before_section = content[:repo_tasks_match.start()]
            after_section = content[repo_tasks_match.end():]
            new_content = before_section + header + modified_tasks + remainder + after_section
            
            # Write back to file
            with open(checklist_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self._debug_print(f"successfully reset tasks in {checklist_path}")
            return True
            
        except Exception as e:
            self._debug_print(f"ERROR: Failed to reset tasks in {checklist_path}: {str(e)}")
            return False
    
    def execute_task(
        self, 
        repo_name: str, 
        checklist_path: str, 
        clone_dir: str = "./clone_repos"
    ) -> Dict[str, Any]:
        """
        Execute tasks for a single repository checklist.
        
        Args:
            repo_name: Name of the repository
            checklist_path: Path to the repository checklist file
            clone_dir: Directory where repositories will be cloned
        
        Returns:
            Dictionary with execution details
        """
        self._debug_print(f"processing repository: {repo_name}")
        
        exit_code, stdout, stderr = self.copilot.execute_prompt(
            'execute-repo-task',
            {'repo_checklist': checklist_path, 'clone': clone_dir}
        )
        
        if exit_code == 0:
            self._debug_print(f"execute-repo-task completed for {repo_name}")
            return {
                "repo_name": repo_name,
                "checklist_path": checklist_path,
                "execution_status": "SUCCESS",
                "exit_code": exit_code,
                "error_message": None
            }
        else:
            self._debug_print(
                f"ERROR: execute-repo-task failed for {repo_name} "
                f"with exit code {exit_code}"
            )
            self._debug_print("continuing to next repository despite failure")
            return {
                "repo_name": repo_name,
                "checklist_path": checklist_path,
                "execution_status": "FAIL",
                "exit_code": exit_code,
                "error_message": (
                    f"execute-repo-task failed with exit code {exit_code}"
                )
            }
    
    def discover_incomplete(self) -> List[Dict[str, str]]:
        """
        Find all repository checklists with incomplete tasks.
        
        Returns:
            List of dictionaries with repo_name and checklist_path
        """
        self._debug_print("discovering repository checklists")
        
        checklist_files = list(self.tasks_dir.glob('*_repo_checklist.md'))
        checklist_files = [
            f for f in checklist_files 
            if f.name != 'all_repository_checklist.md'
        ]
        
        self._debug_print(f"found {len(checklist_files)} repository checklist files")
        
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
        
        self._debug_print(
            f"found {len(incomplete_repos)} repositories with incomplete tasks"
        )
        
        if self.debug and incomplete_repos:
            self._debug_print("repositories to process:")
            for repo in incomplete_repos:
                self._debug_print(f"  - {repo['checklist_path']}")
        
        return incomplete_repos
