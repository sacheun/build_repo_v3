#!/usr/bin/env python3
"""Solution Checklist Readiness Utilities.

Mirrors the behaviour of repo_check_utils for per-solution checklist markdown files.

A solution checklist is considered READY when:
 1. All mandatory tasks are marked completed with [x] in the "## Solution Tasks" section.
 2. All variables whose definitions reference mandatory tasks have non-empty values in the
    "## Solution Variables Available" section.

Assumptions (template-aligned, tolerant to evolution):
  - Mandatory task lines contain the token [MANDATORY] and an @task-* handle.
  - Variable definition lines follow: "- <var_name>: ... (output of @<task-handle>)".
  - Variable value lines in the variables section use either single or double braces and an arrow:
        - {var_name} -> value
        - {{var_name}} → value

Functions:
  check_solution_readiness(path) -> bool
  check_all_solutions(tasks_dir) -> Dict[str,bool]

CLI Usage:
  python tools/solution_check_utils.py <path_to_solution_checklist.md>
  python tools/solution_check_utils.py --dir tasks

Exit code 0 if all requested files are ready, 1 otherwise.
"""
from __future__ import annotations
import os, re, sys
from typing import List, Dict

from checklist_utils import (
    extract_tasks,
    extract_variables,
    classify_variables,
)

# Patterns (similar to repo_check_utils but solution-focused)
MANDATORY_TASK_PATTERN = re.compile(r"^- \[(x| )\].*\[MANDATORY\].*?@([a-zA-Z0-9\-]+)")
RELAXED_TASK_PATTERN = re.compile(r"^- \[(x| )\].*?@([a-zA-Z0-9\-]+)")
SOLUTION_NAME_HEADER_PATTERN = re.compile(r"^# Solution Checklist: *(.+?)\s*$")

def _get_solution_name(lines: List[str]) -> str:
    for line in lines:
        m = SOLUTION_NAME_HEADER_PATTERN.match(line)
        if m:
            return m.group(1).strip() or '<unknown-solution>'
    return '<unknown-solution>'

# Normalization mapping (in case prompt uses synonyms)
TASK_NAME_NORMALIZE = {
    'task-restore-solution': 'task-restore-solution',
    'task-build-solution': 'task-build-solution',
    'execute-solution-task': 'execute-solution-task',  # Allow legacy consolidated task
}

def check_solution_readiness(solution_checklist_path: str) -> bool:
    """Validate a single solution checklist file."""
    if not os.path.isfile(solution_checklist_path):
        print(f"[solution readiness] <missing_file>: FILE_NOT_FOUND path={solution_checklist_path}")
        return False
    with open(solution_checklist_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l.rstrip('\n') for l in f]

    solution_name = _get_solution_name(lines)

    # Support both '## Solution Tasks' and template variant '### Tasks'
    normalize = lambda name: TASK_NAME_NORMALIZE.get(name, name)
    mandatory_tasks = extract_tasks(
        lines,
        ('## Solution Tasks', '### Tasks'),
        MANDATORY_TASK_PATTERN,
        normalize=normalize,
        relaxed_pattern=RELAXED_TASK_PATTERN,
    )

    var_values: Dict[str, str] = extract_variables(
        lines,
        (
            '## Solution Variables Available',
            '## Solution Variables',
            '### Solution Variables'
        )
    )

    # Emit diagnostic detail similar to repo readiness tooling.
    tasks_checked = sorted(mandatory_tasks.keys())
    missing_vars, verified_vars = classify_variables(var_values)
    verified_vars = sorted(verified_vars)
    print(f"[solution readiness detail] {solution_name}: tasks_checked={tasks_checked}")
    print(f"[solution readiness detail] {solution_name}: variables_verified={verified_vars}")

    missing_tasks = [t for t, done in mandatory_tasks.items() if not done]
    missing_vars = sorted(missing_vars)

    if not mandatory_tasks:
        # No tasks discovered at all -> cannot be ready.
        print(f"[solution readiness] {solution_name}: NO_MANDATORY_TASKS_DETECTED")
        return False

    if missing_tasks or missing_vars:
        parts = []
        if missing_tasks:
            parts.append(f"MISSING_TASKS={missing_tasks}")
        if missing_vars:
            parts.append(f"MISSING_VARS={missing_vars}")
        summary = ' '.join(parts)
        print(f"[solution readiness] {solution_name}: {summary}")
        return False

    print(f"[solution readiness] {solution_name}: OK")
    return True


def check_all_solutions(tasks_dir: str) -> Dict[str, bool]:
    """Scan a directory for *_solution_checklist.md files and check each."""
    results: Dict[str, bool] = {}
    if not os.path.isdir(tasks_dir):
        print(f"[solution readiness] <missing_dir>: DIR_NOT_FOUND path={tasks_dir}")
        return results
    for fname in sorted(os.listdir(tasks_dir)):
        if not fname.endswith('_solution_checklist.md'):
            continue
        path = os.path.join(tasks_dir, fname)
        ok = check_solution_readiness(path)
        results[fname] = ok
    return results

__all__ = ["check_solution_readiness", "check_all_solutions"]
