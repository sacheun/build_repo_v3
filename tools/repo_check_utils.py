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
from typing import List, Dict, Tuple

MANDATORY_TASK_PATTERN = re.compile(r"^- \[(x| )\].*\[MANDATORY\].*?@([a-zA-Z0-9\-]+)")
# Include generate-solution-task-checklists which may not have @task- prefix in variable definitions
TASK_NAME_NORMALIZE = {
    'task-clone-repo': 'task-clone-repo',
    'task-find-solutions': 'task-find-solutions',
    'generate-solution-task-checklists': 'generate-solution-task-checklists',
    'task-search-readme': 'task-search-readme',
}
# Extract variable definitions referencing output of tasks
VAR_DEF_PATTERN = re.compile(r"^- ([a-zA-Z0-9_]+):.*\(output of @([a-zA-Z0-9\-]+)\)")
# Extract variables in Repo Variables Available section
# Match either the unicode right arrow (→) or ASCII -> sequence.
VAR_LINE_PATTERN = re.compile(r"^- \{(?:\{)?([a-zA-Z0-9_]+)\}(?:\})? *(?:→|->) *(.*)$")
# Repo name line arrow match (unicode or ASCII), accept single or double braces
REPO_NAME_PATTERN = re.compile(r"^- \{(?:\{)?repo_name\}(?:\})? *(?:→|->) *(.*)$")

SECTION_HEADER_PATTERN = re.compile(r"^## ")

def _extract_section(lines: List[str], header_prefix: str) -> List[str]:
    """Return lines belonging to a section starting with the given header prefix."""
    content: List[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            if line.strip().lower().startswith(header_prefix.lower()):
                in_section = True
                continue
            elif in_section:
                break
        elif in_section:
            content.append(line)
    return content

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

def _expected_solution_prefixes(solutions_line: str, repo_name: str) -> List[str]:
    """Derive expected solution checklist filename prefixes from solutions line value.

    solutions_line example: 'SDKTestApp.sln; ResourceProvider.sln; ...'
    Returns list like ['<repo>_SDKTestApp_solution_checklist.md', ...]
    """
    items = []
    for part in solutions_line.split(';'):
        part = part.strip()
        if not part:
            continue
        if part.endswith('.sln'):
            base = part[:-4]  # remove .sln
        else:
            base = part
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
    tasks_section = _extract_section(lines, '## Repo Tasks')
    mandatory_tasks: Dict[str, bool] = {}
    for line in tasks_section:
        m = MANDATORY_TASK_PATTERN.match(line.strip())
        if m:
            done_flag, task_name = m.groups()
            task_name_norm = TASK_NAME_NORMALIZE.get(task_name, task_name)
            mandatory_tasks[task_name_norm] = (done_flag == 'x')

    # Extract Variable Definitions section
    var_defs_section = _extract_section(lines, '## Variable Definitions')
    mandatory_vars: List[str] = []
    for line in var_defs_section:
        m = VAR_DEF_PATTERN.match(line.strip())
        if m:
            var_name, source_task = m.groups()
            source_task_norm = TASK_NAME_NORMALIZE.get(source_task, source_task)
            if source_task_norm in mandatory_tasks:
                mandatory_vars.append(var_name)

    # Extract Repo Variables Available section values
    repo_vars_section = _extract_section(lines, '## Repo Variables Available')
    var_values: Dict[str, str] = {}
    for line in repo_vars_section:
        m = VAR_LINE_PATTERN.match(line.strip())
        if m:
            var_name, value = m.groups()
            var_values[var_name] = value.strip()

    missing_tasks = [t for t, done in mandatory_tasks.items() if not done]
    missing_vars = [v for v in mandatory_vars if not var_values.get(v)]

    # Additional solution checklist verification:
    # If solutions variable populated, verify that corresponding solution checklist files exist in tasks directory.
    additional_failures: List[str] = []
    solutions_value = var_values.get('solutions')
    if solutions_value:
        tasks_dir = os.path.dirname(checklist_path) or '.'
        repo_name_extracted = repo_name
        expected_files = _expected_solution_prefixes(solutions_value, repo_name_extracted)
        for fname in expected_files:
            fpath = os.path.join(tasks_dir, fname)
            if not os.path.isfile(fpath):
                additional_failures.append(f"missing_solution_checklist:{fname}")

    if not mandatory_tasks:
        print(f"[repo readiness] {repo_name}: NO_MANDATORY_TASKS_DETECTED")
        return False

    if missing_tasks or missing_vars or additional_failures:
        parts = []
        if missing_tasks:
            parts.append(f"MISSING_TASKS={missing_tasks}")
        if missing_vars:
            parts.append(f"MISSING_VARS={missing_vars}")
        if additional_failures:
            parts.append(f"MISSING_SOLUTION_CHECKLISTS={additional_failures}")
        summary = ' '.join(parts)
        print(f"[repo readiness] {repo_name}: {summary}")
        return False

    print(f"[repo readiness] {repo_name}: OK")
    return True

__all__ = ["check_repo_readiness"]

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python repo_check_utils.py <path_to_repo_checklist.md>")
        sys.exit(2)
    path = sys.argv[1]
    ok = check_repo_readiness(path)
    sys.exit(0 if ok else 1)
