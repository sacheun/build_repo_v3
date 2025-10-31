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

import datetime
import re
from pathlib import Path
from typing import List, Dict, Set, Any


class SolutionOperations:
    """Handles all solution-level operations."""
    
    def __init__(
        self,
        tasks_dir: Path,
        copilot_executor,
        debug: bool = False
    ):
        """
        Initialize solution operations.
        
        Args:
            tasks_dir: Directory containing task checklists
            copilot_executor: CopilotExecutor instance for running commands
            debug: Enable debug output
        """
        self.tasks_dir = tasks_dir
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
        
        exit_code, stdout, stderr = self.copilot.execute_prompt(
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
    
    def discover_incomplete(
        self, 
        completed_repo_names: Set[str] = None
    ) -> List[Dict[str, str]]:
        """
        Find all solution checklists with incomplete tasks.
        Optionally filter by completed parent repositories.
        
        Args:
            completed_repo_names: Set of completed repository names to filter by.
                                 If None, returns all incomplete solutions.
        
        Returns:
            List of dictionaries with solution_name, checklist_path, and parent_repo
        """
        self._debug_print("discovering solution checklists")
        
        solution_checklist_files = list(self.tasks_dir.glob('*_solution_checklist.md'))
        self._debug_print(f"found {len(solution_checklist_files)} solution checklist files")
        
        incomplete_solutions = []
        
        for checklist_path in solution_checklist_files:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract repository name from solution checklist filename
            # Format: {org}_{repo}_{solution}_solution_checklist.md
            solution_filename = checklist_path.stem.replace('_solution_checklist', '')
            
            # Determine the repository name this solution belongs to
            belongs_to_completed_repo = False
            parent_repo = None
            
            if completed_repo_names:
                for repo_name in completed_repo_names:
                    # Check if solution name starts with repo name
                    if solution_filename.startswith(repo_name):
                        belongs_to_completed_repo = True
                        parent_repo = repo_name
                        break
                
                # Skip solutions from incomplete repositories
                if not belongs_to_completed_repo:
                    self._debug_print(
                        f"Skipping solution {solution_filename} - "
                        "parent repository not completed"
                    )
                    continue
            
            # Find Tasks section using regex (solution checklists use ### Tasks)
            solution_tasks_match = re.search(
                r'### Tasks.*?\n(.*?)(?=\n##|\Z)', 
                content, 
                re.DOTALL
            )
            
            if solution_tasks_match:
                solution_tasks_section = solution_tasks_match.group(1)
                
                # Check for incomplete tasks
                if re.search(r'- \[ \]', solution_tasks_section):
                    solution_name = checklist_path.stem.replace('_solution_checklist', '')
                    incomplete_solutions.append({
                        'solution_name': solution_name,
                        'checklist_path': str(checklist_path),
                        'parent_repo': parent_repo
                    })
        
        if completed_repo_names:
            self._debug_print(
                f"found {len(incomplete_solutions)} solution checklists with incomplete tasks "
                f"from completed repositories"
            )
        else:
            self._debug_print(
                f"found {len(incomplete_solutions)} solution checklists with incomplete tasks"
            )
        
        if self.debug and incomplete_solutions:
            self._debug_print("solution checklists to process:")
            for solution in incomplete_solutions:
                self._debug_print(f"  - {solution['checklist_path']}")
        
        return incomplete_solutions
