#!/usr/bin/env python3
"""Repository Checklist Readiness Utilities.

Provides a function to verify that a repository checklist markdown file has:
 1. All mandatory tasks marked completed `[x]`.
 2. All variables produced by mandatory tasks populated (non-empty value after the arrow).

Usage:
    from repo_check_utils import check_repo_readiness
    ok = check_repo_readiness('tasks/ic3_spool_cosine-dep-spool_repo_checklist.md')

The function prints a one-line summary per file to console:
    [repo readiness] <repo_name>: OK
or
    [repo readiness] <repo_name>: MISSING_TASKS=[t1,t2] MISSING_VARS=[v1,v2]

Return:
    True if all mandatory tasks completed AND all mandatory variables populated.
    False otherwise.
"""
from __future__ import annotations
import os, re
from typing import List, Dict

from checklist_utils import (
    extract_tasks,
    extract_variables,
    classify_variables,
)

MANDATORY_TASK_PATTERN = re.compile(r"^- \[(x| )\].*\[MANDATORY\].*?@([a-zA-Z0-9\-]+)")
# Include generate-solution-task-checklists which may not have @task- prefix in variable definitions
TASK_NAME_NORMALIZE = {
    'task-clone-repo': 'task-clone-repo',
    'task-find-solutions': 'task-find-solutions',
    'generate-solution-task-checklists': 'generate-solution-task-checklists',
    'task-search-readme': 'task-search-readme',
}
# Repo name line arrow match (unicode or ASCII), accept single or double braces
REPO_NAME_PATTERN = re.compile(r"^- \{(?:\{)?repo_name\}(?:\})? *(?:→|->) *(.*)$")

def _get_repo_name(lines: List[str]) -> str:
    for line in lines:
        if line.startswith("- {repo_name}") or line.startswith("- {{repo_name}}"):  # accept single or double brace form
            m = REPO_NAME_PATTERN.match(line)
            if m:
                return m.group(1).strip() or "<unknown>"
    # Fallback: parse header line '# Task Checklist: name'
    for line in lines:
        if line.startswith('# Task Checklist:'):
            return line.partition(':')[2].strip() or '<unknown>'
    return '<unknown>'

def _expected_solution_checklist_filenames(solutions_line: str, repo_name: str) -> List[str]:
    """Derive expected checklist filenames from the solutions variable value."""
    items: List[str] = []
    for part in re.split(r"[;\n,]+", solutions_line):
        part = part.strip()
        if not part:
            continue
        base = part[:-4] if part.lower().endswith('.sln') else part
        items.append(f"{repo_name}_{base}_solution_checklist.md")
    return items

def check_repo_readiness(checklist_path: str) -> bool:
    """Check if a repo checklist is ready for conditional tasks.

    Steps:
      1. Parse mandatory tasks and verify all are marked with [x].
      2. Identify variables produced by mandatory tasks from Variable Definitions.
      3. Verify those variables have non-empty values in Repo Variables Available section.
    """
    if not os.path.isfile(checklist_path):
        print(f"[repo readiness] <missing_file>: FILE_NOT_FOUND path={checklist_path}")
        return False
    with open(checklist_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l.rstrip('\n') for l in f]

    repo_name = _get_repo_name(lines)

    # Extract Repo Tasks section
    normalize = lambda name: TASK_NAME_NORMALIZE.get(name, name)
    mandatory_tasks = extract_tasks(
        lines,
        ('## Repo Tasks',),
        MANDATORY_TASK_PATTERN,
        normalize=normalize
    )

    var_values: Dict[str, str] = extract_variables(lines, ('## Repo Variables Available',))

    missing_tasks = [t for t, done in mandatory_tasks.items() if not done]
    # Treat executed_commands and skipped_commands as optional even if their producing task is mandatory.
    OPTIONAL_VARS = {'executed_commands', 'skipped_commands'}
    missing_vars, verified_vars = classify_variables(var_values, optional=OPTIONAL_VARS)
    missing_vars = sorted(missing_vars)
    verified_vars = sorted(verified_vars)

    # Additional solution checklist verification:
    # If solutions variable populated, verify that corresponding solution checklist files exist in tasks directory.
    additional_failures: List[str] = []
    solutions_value = var_values.get('solutions')
    if solutions_value and 'solutions' not in missing_vars:
        tasks_dir = os.path.dirname(checklist_path) or '.'
        repo_name_extracted = repo_name
        expected_files = _expected_solution_checklist_filenames(solutions_value, repo_name_extracted)
        for fname in expected_files:
            fpath = os.path.join(tasks_dir, fname)
            if not os.path.isfile(fpath):
                additional_failures.append(f"missing_solution_checklist:{fname}")

    if not mandatory_tasks:
        print(f"[repo readiness] {repo_name}: NO_MANDATORY_TASKS_DETECTED")
        return False

    if missing_tasks or missing_vars or additional_failures:
        if missing_tasks:
            print(f"[repo readiness] {repo_name}: MISSING_TASKS={missing_tasks}")
        if missing_vars:
            print(f"[repo readiness] {repo_name}: MISSING_VARS={missing_vars}")
        if additional_failures:
            print(f"[repo readiness] {repo_name}: MISSING_SOLUTION_CHECKLISTS={additional_failures}")
        return False

    # Successful readiness; emit detail lines to clarify what was validated.
    verified_tasks = sorted(mandatory_tasks.keys())
    if verified_tasks:
        print(f"[repo readiness detail] {repo_name}: tasks_checked={verified_tasks}")
    if verified_vars:
        print(f"[repo readiness detail] {repo_name}: variables_verified={verified_vars}")
    print(f"[repo readiness] {repo_name}: OK")
    return True

__all__ = ["check_repo_readiness"]
