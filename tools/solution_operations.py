#!/usr/bin/env python3
"""
Solution Operations Module

This module provides functions for solution-level operations including:
- Resetting solution tasks
- Executing solution tasks  
- Discovering incomplete solutions
- Filtering solutions by parent repository

Usage:
    from solution_operations import SolutionOperations
    
    sol_ops = SolutionOperations(
        tasks_dir='./tasks',
        copilot_executor=copilot,
        debug=True
    )
    
    # Execute solution tasks
    result = sol_ops.execute_task('my_solution', './tasks/my_solution_checklist.md')
    
    # Discover incomplete solutions
    incomplete = sol_ops.discover_incomplete(completed_repo_names={'repo1', 'repo2'})
"""

import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class SolutionOperations:
    """Handles all solution-level operations."""
    
    def __init__(
        self,
        tasks_dir: Path,
        results_dir: Path,
        copilot_executor,
        debug: bool = False
    ):
        """
        Initialize solution operations.
        
        Args:
            tasks_dir: Directory containing task checklists
            results_dir: Directory containing results CSV files
            copilot_executor: CopilotExecutor instance for running commands
            debug: Enable debug output
        """
        self.tasks_dir = tasks_dir
        self.results_dir = results_dir
        self.copilot = copilot_executor
        self.debug = debug
    
    def _debug_print(self, message: str):
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"[debug][solution-operations] {message}")
    
    def reset_tasks(self, checklist_path: Path) -> bool:
        """
        Reset incomplete tasks in a solution checklist from [x] to [ ].
        
        Args:
            checklist_path: Path to the solution checklist file
        
        Returns:
            True if tasks were reset successfully, False otherwise
        """
        self._debug_print(f"resetting tasks in {checklist_path}")
        
        try:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Tasks section (solution checklists use ### Tasks)
            tasks_match = re.search(
                r'(### Tasks.*?\n)(.*?)((?=\n##|\Z))',
                content,
                re.DOTALL
            )
            
            if not tasks_match:
                self._debug_print(f"ERROR: Could not find Tasks section in {checklist_path}")
                return False
            
            header = tasks_match.group(1)
            tasks_section = tasks_match.group(2)
            remainder = tasks_match.group(3)
            
            # Reset all completed tasks to incomplete
            modified_tasks = re.sub(r'- \[x\]', '- [ ]', tasks_section)
            
            # Reconstruct the content
            before_section = content[:tasks_match.start()]
            after_section = content[tasks_match.end():]
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
        solution_name: str, 
        solution_checklist_path: str
    ) -> Dict[str, Any]:
        """
        Execute tasks for a single solution checklist.
        
        Args:
            solution_name: Name of the solution (without _solution_checklist.md suffix)
            solution_checklist_path: Path to the solution checklist file
        
        Returns:
            Dictionary with execution details
        """
        self._debug_print(f"processing solution: {solution_name}")
        
        exit_code, _stdout, _stderr = self.copilot.execute_prompt(
            'execute-solution-task',
            {'solution_checklist': solution_checklist_path}
        )
        
        if exit_code == 0:
            self._debug_print(f"execute-solution-task completed for {solution_name}")
            return {
                "solution_name": solution_name,
                "checklist_path": solution_checklist_path,
                "execution_status": "SUCCESS",
                "exit_code": exit_code,
                "error_message": None
            }
        else:
            self._debug_print(
                f"ERROR: execute-solution-task failed for {solution_name} "
                f"with exit code {exit_code}"
            )
            self._debug_print("continuing to next solution despite failure")
            return {
                "solution_name": solution_name,
                "checklist_path": solution_checklist_path,
                "execution_status": "FAIL",
                "exit_code": exit_code,
                "error_message": (
                    f"execute-solution-task failed with exit code {exit_code}"
                )
            }

    def _load_solution_result_entries(self) -> List[Dict[str, str]]:
        """Load normalized entries from solution results CSV files."""
        entries: List[Dict[str, str]] = []
        candidate_files = [
            self.results_dir / 'solution-results.csv',
            self.results_dir / 'solution_result.csv'
        ]

        for csv_path in candidate_files:
            if not csv_path.exists():
                continue

            try:
                with open(csv_path, 'r', encoding='utf-8', newline='') as handle:
                    reader = csv.DictReader(handle)
                    if not reader.fieldnames:
                        continue

                    for row in reader:
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
                        task_value = (
                            row.get('task name')
                            or row.get('task_name')
                            or row.get('task')
                            or row.get('Task Name')
                            or ''
                        ).strip()

                        if repo_value and solution_value and task_value:
                            entries.append({
                                'repo': repo_value,
                                'solution': solution_value,
                                'task': task_value,
                                'source': csv_path.name
                            })

            except Exception as exc:  # noqa: BLE001
                self._debug_print(
                    f"ERROR: failed to read {csv_path.name} for verification: {exc}"
                )

        return entries

    def verify_tasks_completed(
        self,
        repo_filter: Optional[Set[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate solution checklists and solution results tracking.

        Args:
            repo_filter: Optional set of repository names to include.

        Returns:
            List of solutions that failed verification with details.
        """

        solution_files = list(self.tasks_dir.glob('*_solution_checklist.md'))
        entries = self._load_solution_result_entries()
        csv_available = bool(entries)
        incomplete_solutions: List[Dict[str, Any]] = []

        for checklist_path in solution_files:
            try:
                content = checklist_path.read_text(encoding='utf-8')
            except OSError as exc:
                self._debug_print(
                    f"ERROR: unable to read checklist {checklist_path}: {exc}"
                )
                incomplete_solutions.append({
                    'repo_name': None,
                    'solution_display_name': None,
                    'solution_slug': checklist_path.stem.replace('_solution_checklist', ''),
                    'checklist_path': str(checklist_path.resolve()),
                    'incomplete_tasks': ['failed to read checklist file']
                })
                continue

            repo_match = re.search(r'^Repository:\s*(.+)$', content, re.MULTILINE)
            display_match = re.search(r'^# Solution Checklist:\s*(.+)$', content, re.MULTILINE)
            tasks_match = re.search(r'### Tasks.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)

            repo_name = repo_match.group(1).strip() if repo_match else None
            display_name = display_match.group(1).strip() if display_match else None
            slug_name = checklist_path.stem.replace('_solution_checklist', '')

            if repo_filter and repo_name and repo_name not in repo_filter:
                continue

            issues: List[str] = []

            if not repo_name:
                issues.append('repository name missing in checklist header')
            if not display_name:
                issues.append('solution display name missing in checklist header')
            if not tasks_match:
                issues.append('Tasks section missing from checklist')

            completed_mandatory: List[str] = []
            incomplete_mandatory: List[str] = []

            if tasks_match:
                tasks_section = tasks_match.group(1)
                mandatory_matches = re.findall(
                    r'- \[(x| )\] \[MANDATORY[^\]]*\].*?(@\S+)',
                    tasks_section
                )

                for state, task_ref in mandatory_matches:
                    normalized_task = task_ref.strip()
                    if state.lower() == 'x':
                        completed_mandatory.append(normalized_task)
                    else:
                        incomplete_mandatory.append(normalized_task)

                for task in incomplete_mandatory:
                    issues.append(f"MANDATORY task incomplete: {task}")

                identifier_candidates = {display_name, slug_name}
                if '_' in slug_name:
                    suffix = slug_name.split('_', 1)[1]
                    identifier_candidates.add(suffix)
                    identifier_candidates.add(suffix.replace('_', ' '))
                    identifier_candidates.add(suffix.replace('_', '.'))
                if display_name:
                    identifier_candidates.add(display_name.replace('_', ' '))
                    identifier_candidates.add(display_name.replace('_', '.'))

                identifier_set = {
                    ident.strip()
                    for ident in identifier_candidates
                    if ident and ident.strip()
                }
                identifier_lower = {ident.lower() for ident in identifier_set}

                repo_key = repo_name.strip() if repo_name else None

                if completed_mandatory and repo_key:
                    for task_ref in completed_mandatory:
                        base_task = task_ref.lstrip('@')
                        task_candidates = {task_ref, base_task}
                        task_lower = {candidate.lower() for candidate in task_candidates}
                        match_count = 0
                        for entry in entries:
                            if entry['repo'].strip() != repo_key:
                                continue

                            solution_value = entry['solution'].strip()
                            if identifier_set and (
                                solution_value not in identifier_set
                                and solution_value.lower() not in identifier_lower
                            ):
                                continue

                            entry_task = entry['task'].strip()
                            normalized_entry_task = entry_task.lstrip('@')
                            if (
                                entry_task not in task_candidates
                                and entry_task.lower() not in task_lower
                                and normalized_entry_task not in task_candidates
                                and normalized_entry_task.lower() not in task_lower
                            ):
                                continue

                            match_count += 1

                        if match_count == 0:
                            issues.append(
                                f"CSV entry missing for {task_ref}"
                            )
                        elif match_count > 1:
                            issues.append(
                                f"CSV entry count {match_count} (expected 1) for {task_ref}"
                            )

                if completed_mandatory and not csv_available:
                    issues.append('solution-results.csv not found or empty')

            if issues:
                incomplete_solutions.append({
                    'repo_name': repo_name,
                    'solution_display_name': display_name,
                    'solution_slug': slug_name,
                    'checklist_path': str(checklist_path.resolve()),
                    'incomplete_tasks': issues,
                    'completed_mandatory_tasks': completed_mandatory,
                    'incomplete_mandatory_tasks': incomplete_mandatory
                })

        return incomplete_solutions
    
    def discover_incomplete(
        self,
        completed_repo_names: Set[str] = None,
        ignore_repo_completion: bool = False
    ) -> List[Dict[str, str]]:
        """
        Identify solution checklists that require processing.

        A solution is considered incomplete when verification detects
        outstanding mandatory tasks or missing CSV rows. Optional tasks
        are ignored so behaviour mirrors repository processing.

        Args:
            completed_repo_names: Optional set of repository names to include.
            ignore_repo_completion: If True, process solutions regardless of repo completion status.

        Returns:
            List of dictionaries with solution_name, checklist_path, and parent_repo.
        """

        self._debug_print("discovering solution checklists")

        repo_filter = None
        if completed_repo_names and not ignore_repo_completion:
            repo_filter = {name.strip() for name in completed_repo_names if name}

        verification_results = self.verify_tasks_completed(repo_filter=repo_filter)
        verification_map: Dict[Path, Dict[str, Any]] = {}
        for entry in verification_results:
            checklist_value = entry.get('checklist_path')
            if not checklist_value:
                continue

            resolved_path = Path(checklist_value).resolve()
            verification_map[resolved_path] = entry

        solution_checklist_files = list(self.tasks_dir.glob('*_solution_checklist.md'))
        self._debug_print(
            f"found {len(solution_checklist_files)} solution checklist files"
        )

        incomplete_solutions: List[Dict[str, str]] = []

        for checklist_path in solution_checklist_files:
            resolved_path = checklist_path.resolve()
            verification_entry = verification_map.get(resolved_path)

            if not verification_entry:
                continue

            slug_name = checklist_path.stem.replace('_solution_checklist', '')
            repo_name = verification_entry.get('repo_name')
            
            # If ignoring repo completion, derive repo name from slug and include all solutions
            if ignore_repo_completion:
                if not repo_name:
                    # Try to derive repo name from solution name
                    if completed_repo_names:
                        repo_name = next(
                            (candidate for candidate in completed_repo_names if slug_name.startswith(candidate)),
                            slug_name  # Use slug name as fallback
                        )
                    else:
                        repo_name = slug_name
            elif repo_filter:
                if repo_name and repo_name not in repo_filter:
                    derived_repo = next(
                        (candidate for candidate in repo_filter if slug_name.startswith(candidate)),
                        None
                    )
                    if not derived_repo:
                        continue
                    repo_name = derived_repo
                elif not repo_name:
                    repo_name = next(
                        (candidate for candidate in repo_filter if slug_name.startswith(candidate)),
                        None
                    )
                    if not repo_name:
                        continue
                        
            incomplete_solutions.append({
                'solution_name': slug_name,
                'checklist_path': str(checklist_path),
                'parent_repo': repo_name
            })

        self._debug_print(
            f"found {len(incomplete_solutions)} solution checklists with verification issues"
        )

        if self.debug and incomplete_solutions:
            self._debug_print("solution checklists to process:")
            for solution in incomplete_solutions:
                self._debug_print(f"  - {solution['checklist_path']}")

        return incomplete_solutions
