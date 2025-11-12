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
from typing import List, Dict, Tuple

# Patterns (similar to repo_check_utils but solution-focused)
MANDATORY_TASK_PATTERN = re.compile(r"^- \[(x| )\].*\[MANDATORY\].*?@([a-zA-Z0-9\-]+)")
VAR_DEF_PATTERN = re.compile(r"^- ([a-zA-Z0-9_]+):.*\(output of @([a-zA-Z0-9\-]+)\)")
VAR_LINE_PATTERN = re.compile(r"^- \{(?:\{)?([a-zA-Z0-9_]+)\}(?:\})? *(?:→|->) *(.*)$")
SOLUTION_NAME_HEADER_PATTERN = re.compile(r"^# Solution Checklist: *(.+?)\s*$")

SECTION_HEADER_PREFIX = "## "

def _extract_section(lines: List[str], header_prefix: str) -> List[str]:
    """Return lines belonging to a section starting with the given header prefix.

    Accepts either level 2 (##) or level 3 (###) headers to tolerate checklist template variants.
    """
    content: List[str] = []
    in_section = False
    header_prefix_lower = header_prefix.lower()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') or stripped.startswith('### '):
            # Normalize both forms for comparison
            lower = stripped.lower()
            if lower.startswith(header_prefix_lower):
                in_section = True
                continue
            elif in_section:
                break
        elif in_section:
            content.append(line)
    return content

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
    tasks_section = _extract_section(lines, '## Solution Tasks')
    if not tasks_section:
        tasks_section = _extract_section(lines, '### Tasks')
    mandatory_tasks: Dict[str, bool] = {}
    for line in tasks_section:
        m = MANDATORY_TASK_PATTERN.match(line.strip())
        if m:
            done_flag, task_name = m.groups()
            task_name_norm = TASK_NAME_NORMALIZE.get(task_name, task_name)
            mandatory_tasks[task_name_norm] = (done_flag == 'x')

    # Fallback: if no explicit [MANDATORY] markers found but tasks_section has content,
    # treat every listed task line as mandatory (uses relaxed pattern without [MANDATORY]).
    if not mandatory_tasks and tasks_section:
        RELAXED_TASK_PATTERN = re.compile(r"^- \[(x| )\].*?@([a-zA-Z0-9\-]+)")
        for line in tasks_section:
            m2 = RELAXED_TASK_PATTERN.match(line.strip())
            if m2:
                done_flag, task_name = m2.groups()
                task_name_norm = TASK_NAME_NORMALIZE.get(task_name, task_name)
                # Avoid overwriting in case of duplicates
                if task_name_norm not in mandatory_tasks:
                    mandatory_tasks[task_name_norm] = (done_flag == 'x')

    var_defs_section = _extract_section(lines, '## Variable Definitions')
    mandatory_vars: List[str] = []
    for line in var_defs_section:
        m = VAR_DEF_PATTERN.match(line.strip())
        if m:
            var_name, source_task = m.groups()
            source_task_norm = TASK_NAME_NORMALIZE.get(source_task, source_task)
            if source_task_norm in mandatory_tasks:
                mandatory_vars.append(var_name)

    vars_section = _extract_section(lines, '## Solution Variables Available')
    var_values: Dict[str, str] = {}
    for line in vars_section:
        m = VAR_LINE_PATTERN.match(line.strip())
        if m:
            var_name, value = m.groups()
            var_values[var_name] = value.strip()

    missing_tasks = [t for t, done in mandatory_tasks.items() if not done]
    missing_vars = [v for v in mandatory_vars if not var_values.get(v)]

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

if __name__ == '__main__':
    if '--dir' in sys.argv:
        try:
            dir_index = sys.argv.index('--dir')
            tasks_dir = sys.argv[dir_index + 1]
        except Exception:
            print('Usage: python solution_check_utils.py --dir <tasks_dir>')
            sys.exit(2)
        results = check_all_solutions(tasks_dir)
        # Exit code 0 only if all present solution checklists passed
        if results and all(results.values()):
            sys.exit(0)
        sys.exit(1)
    elif len(sys.argv) >= 2:
        path = sys.argv[1]
        ok = check_solution_readiness(path)
        sys.exit(0 if ok else 1)
    else:
        print('Usage: python solution_check_utils.py <path_to_solution_checklist.md> | --dir <tasks_dir>')
        sys.exit(2)
