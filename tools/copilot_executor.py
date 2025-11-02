#!/usr/bin/env python3
"""
Copilot Command Executor

This module provides utilities for executing GitHub Copilot commands via subprocess.
All command output is logged to a specified log file for debugging and audit purposes.

Usage:
    from copilot_executor import CopilotExecutor
    
    executor = CopilotExecutor(log_file='./my_log.log', debug=True)
    exit_code, stdout, stderr = executor.execute_prompt(
        prompt_name='task-clone-repo',
        params={'repo_url': 'https://github.com/...', 'clone_dir': './repos'}
    )
"""

import datetime
import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Optional


class CopilotExecutor:
    """Executor for GitHub Copilot commands with logging support."""
    
    def __init__(self, log_file: str = './copilot_executor.log', debug: bool = False):
        """
        Initialize the Copilot executor.
        
        Args:
            log_file: Path to the log file where all command output will be written
            debug: If True, print debug messages to console
        """
        self.log_file = Path(log_file)
        self.debug = debug
        
    def _debug_print(self, message: str):
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"[debug][copilot-executor] {message}")
    
    def _log_to_file(self, message: str):
        """Append message to log file."""
        with open(self.log_file, 'a', encoding='utf-8') as log:
            log.write(message)
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a raw copilot command using subprocess.
        Logs all output to the configured log file.
        
        Args:
            command: The full command string to execute
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        self._debug_print(f"executing: {command}")
        
        # Log command to file
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._log_to_file(f"\n{'='*80}\n")
        self._log_to_file(f"[{timestamp}] Executing command:\n")
        self._log_to_file(f"{command}\n")
        self._log_to_file(f"{'='*80}\n\n")
        
        # Execute command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
        except subprocess.TimeoutExpired:
            self._log_to_file(f"ERROR: Command timed out after 1800 seconds\n\n")
            self._debug_print("command timed out after 30 minutes")
            return -1, "", "Command timed out after 1800 seconds"
        
        # Log output to file
        self._log_to_file(f"Exit Code: {result.returncode}\n\n")

        if result.stdout:
            self._log_to_file("STDOUT:\n")
            self._log_to_file(result.stdout)
            self._log_to_file("\n\n")

        if result.stderr:
            self._log_to_file("STDERR:\n")
            self._log_to_file(result.stderr)
            self._log_to_file("\n\n")

        if result.returncode != 0:
            print(
                (
                    "[error][copilot-executor] command failed with exit code "
                    f"{result.returncode}"
                )
            )
            if result.stderr:
                print("[error][copilot-executor] stderr:")
                print(result.stderr.strip())

        return result.returncode, result.stdout, result.stderr
    
    def execute_prompt(
        self, 
        prompt_name: str, 
        params: Optional[Dict[str, str]] = None,
        allow_all_tools: bool = True
    ) -> Tuple[int, str, str]:
        """
        Execute a GitHub Copilot prompt with parameters.
        
        Args:
            prompt_name: Name of the prompt (e.g., 'task-clone-repo', 'execute-repo-task')
            params: Dictionary of parameter name-value pairs to pass to the prompt
            allow_all_tools: If True, adds --allow-all-tools flag
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
            
        Example:
            execute_prompt(
                'execute-repo-task',
                {'repo_checklist': 'tasks/myrepo_checklist.md', 'clone': './clone_repos'}
            )
            # Executes: copilot --prompt "/execute-repo-task repo_checklist=\"...\" clone=\"...\"" --allow-all-tools
        """
        # Read copilot-instructions.md content
        instructions_content = """
        *** Important ***
        1. Execute the tasks in the markdown file one task at a time. Do not skip any task. Do not group scriptable and non scriptable tasks in 1 script."
        """
        
        # Build parameter string
        param_str = ""
        if params:
            sanitized = []
            for key, value in params.items():
                safe_value = str(value).replace("'", "\\'")
                sanitized.append(f"{key}='{safe_value}'")
            param_parts = sanitized
            param_str = " " + " ".join(param_parts)
        
        # Build prompt with instructions first, then task
        prompt_parts = []
        #if instructions_content:
        #    prompt_parts.append(instructions_content)
        #prompt_parts.append("Now perform task:")
        prompt_parts.append(f"/{prompt_name}{param_str}")

        # for some reason, these does not work. it just hjangs
        #if instructions_content:
        #    prompt_parts.append("\n")
        #    prompt_parts.append(instructions_content)
        #prompt_parts.append("Now perform task:")

        full_prompt = "\n".join(prompt_parts)
        
        # Build full command
        command = f'copilot --prompt "{full_prompt}"'
        if allow_all_tools:
            command += ' --allow-all-tools'
        command += ' --allow-all-paths'
        
        return self.execute_command(command)
    
    def initialize_log(self, header: str):
        """
        Initialize the log file with a header.
        
        Args:
            header: Header text to write at the beginning of the log file
        """
        with open(self.log_file, 'w', encoding='utf-8') as log:
            log.write(header)
            log.write(f"\n{'='*80}\n\n")


# Convenience function for backwards compatibility
def execute_copilot_command(
    command: str, 
    log_file: str = './copilot_executor.log',
    debug: bool = False
) -> Tuple[int, str, str]:
    """
    Execute a copilot command (convenience function).
    
    Args:
        command: The full command string to execute
        log_file: Path to the log file
        debug: Enable debug output
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    executor = CopilotExecutor(log_file=log_file, debug=debug)
    return executor.execute_command(command)


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python copilot_executor.py <command>")
        print("Example: python copilot_executor.py 'copilot --prompt \"/help\"'")
        sys.exit(1)
    
    command = sys.argv[1]
    executor = CopilotExecutor(debug=True)
    exit_code, stdout, stderr = executor.execute_command(command)
    
    print(f"\nExit Code: {exit_code}")
    if stdout:
        print(f"STDOUT:\n{stdout}")
    if stderr:
        print(f"STDERR:\n{stderr}")
    
    sys.exit(exit_code)
