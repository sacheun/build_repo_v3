#!/usr/bin/env python3
"""Shared helpers for checklist readiness utilities."""
from __future__ import annotations
import re
from typing import Iterable, List, Optional, Sequence, Tuple, Dict, Callable

_SECTION_PREFIXES = ("## ", "### ")
_VAR_ARROW_PATTERN = re.compile(r"^- \{(?:\{)?([a-zA-Z0-9_]+)\}(?:\})? *(?:→|->) *(.*)$")
_VAR_COLON_PATTERN = re.compile(r"^- *([a-zA-Z0-9_]+)\s*[:=]\s*(.*)$")
_BLANK_VALUE_MARKERS = {'', '(blank)', 'blank', 'n/a', 'na', '(none)'}


def collect_section_lines(lines: Sequence[str], headers: Iterable[str]) -> List[str]:
    """Collect lines belonging to the first section whose header matches any provided prefix."""
    header_variants = tuple(h.lower() for h in headers)
    content: List[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(prefix) for prefix in _SECTION_PREFIXES):
            lower = stripped.lower()
            if any(lower.startswith(h) for h in header_variants):
                in_section = True
                continue
            if in_section:
                break
        elif in_section:
            content.append(line)
    return content


def parse_variable_line(line: str) -> Optional[Tuple[str, str]]:
    """Parse a checklist variable line and return (name, value) or None."""
    stripped = line.strip()
    if not stripped.startswith('- '):
        return None
    if stripped.startswith('- ['):
        return None
    arrow_match = _VAR_ARROW_PATTERN.match(stripped)
    if arrow_match:
        var_name, value = arrow_match.groups()
        return var_name.strip(), value.strip()
    colon_match = _VAR_COLON_PATTERN.match(stripped)
    if colon_match:
        var_name, value = colon_match.groups()
        return var_name.strip(), value.strip()
    return None


def is_blank_value(value: Optional[str]) -> bool:
    """Return True when the provided value should be treated as blank."""
    if value is None:
        return True
    return value.strip().lower() in _BLANK_VALUE_MARKERS


def extract_tasks(
    lines: Sequence[str],
    headers: Iterable[str],
    mandatory_pattern: re.Pattern[str],
    *,
    normalize: Optional[Callable[[str], str]] = None,
    relaxed_pattern: Optional[re.Pattern[str]] = None,
) -> Dict[str, bool]:
    """Extract mandatory tasks from the specified section using provided patterns."""
    section = collect_section_lines(lines, headers)
    tasks: Dict[str, bool] = {}
    for line in section:
        match = mandatory_pattern.match(line.strip())
        if match:
            done_flag, task_name = match.groups()
            key = normalize(task_name) if normalize else task_name
            if key not in tasks:
                tasks[key] = (done_flag == 'x')

    if not tasks and relaxed_pattern:
        for line in section:
            match = relaxed_pattern.match(line.strip())
            if match:
                done_flag, task_name = match.groups()
                key = normalize(task_name) if normalize else task_name
                if key not in tasks:
                    tasks[key] = (done_flag == 'x')
    return tasks


def extract_variables(lines: Sequence[str], headers: Iterable[str]) -> Dict[str, str]:
    """Return a mapping of variable names to their recorded values from the given sections."""
    section = collect_section_lines(lines, headers)
    values: Dict[str, str] = {}
    for line in section:
        parsed = parse_variable_line(line)
        if parsed:
            name, value = parsed
            if name not in values:
                values[name] = value.strip()
    return values


def classify_variables(
    var_values: Dict[str, str],
    *,
    optional: Optional[Iterable[str]] = None,
) -> Tuple[List[str], List[str]]:
    """Split variables into missing and verified lists, ignoring optional entries."""
    optional_set = set(optional or ())
    missing: List[str] = []
    verified: List[str] = []
    for name, value in var_values.items():
        if name in optional_set:
            continue
        if is_blank_value(value):
            missing.append(name)
        else:
            verified.append(name)
    return missing, verified


__all__ = [
    'collect_section_lines',
    'parse_variable_line',
    'is_blank_value',
    'extract_tasks',
    'extract_variables',
    'classify_variables',
]
