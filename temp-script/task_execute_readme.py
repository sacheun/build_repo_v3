import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

repo_dir = r'C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool'
repo_name = 'ic3_spool_cosine-dep-spool'
DEBUG = os.environ.get('DEBUG', '0') == '1'

if DEBUG:
    print(f'[debug][task-execute-readme] START repo_directory="{repo_dir}"')

# README candidate filenames in priority order
readme_candidates = ['README.md', 'readme.md', 'README.txt', 'README.rst', 'README', 'Readme.md']

readme_content = None
readme_filename = None
setup_commands_executed = []
setup_commands_skipped = []

# Search for README file
for candidate in readme_candidates:
    if DEBUG:
        print(f'[debug][task-execute-readme] checking for: {candidate}')
    
    readme_path = Path(repo_dir) / candidate
    if readme_path.exists():
        readme_filename = candidate
        if DEBUG:
            print(f'[debug][task-execute-readme] found README file: {readme_filename}')
        
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
            
            if DEBUG:
                print(f'[debug][task-execute-readme] content length: {len(readme_content)} characters')
        except Exception as e:
            print(f'[run10][execute-readme] Error reading README: {e}')
            readme_content = None
        
        break

if readme_filename is None and DEBUG:
    print('[debug][task-execute-readme] no README file found in repository root')

# Step 5: Structural Reasoning and Setup Command Parsing
if readme_content:
    # Section headings to look for (case-insensitive)
    section_patterns = [
        r'#+\s*(Prerequisites?|Before\s+you\s+build|Setup|Local\s+dev|Getting\s+Started|Installation|Requirements?)',
        r'\*\*\s*(Prerequisites?|Before\s+you\s+build|Setup|Local\s+dev|Getting\s+Started|Installation|Requirements?)\s*\*\*'
    ]
    
    # Find relevant sections
    relevant_text = []
    lines = readme_content.split('\n')
    in_relevant_section = False
    
    for i, line in enumerate(lines):
        # Check if line is a section header
        is_section_header = False
        for pattern in section_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                in_relevant_section = True
                is_section_header = True
                break
        
        # Check if we've left the relevant section (new heading)
        if in_relevant_section and not is_section_header:
            if re.match(r'^#+\s+', line) or re.match(r'^\*\*[^*]+\*\*$', line):
                # New section started, stop if it's not a relevant section
                if not any(re.search(p, line, re.IGNORECASE) for p in section_patterns):
                    in_relevant_section = False
            else:
                relevant_text.append(line)
    
    # Extract commands from relevant sections
    commands = []
    
    # Pattern 1: Fenced code blocks
    code_block_pattern = r'```(?:bash|sh|shell|powershell|ps1|cmd)?\n(.*?)\n```'
    for match in re.finditer(code_block_pattern, '\n'.join(relevant_text), re.DOTALL):
        code = match.group(1).strip()
        for cmd_line in code.split('\n'):
            cmd_line = cmd_line.strip()
            if cmd_line and not cmd_line.startswith('#') and not cmd_line.startswith('//'):
                commands.append(cmd_line)
    
    # Pattern 2: Inline code with command indicators
    inline_pattern = r'`([^`]+)`'
    for match in re.finditer(inline_pattern, '\n'.join(relevant_text)):
        cmd = match.group(1).strip()
        # Check if it looks like a command (contains npm, pip, dotnet, etc.)
        if any(keyword in cmd.lower() for keyword in ['npm ', 'pip ', 'dotnet ', 'nuget ', 'git ', 'node ', 'python ']):
            commands.append(cmd)
    
    # Classify and execute commands
    safe_keywords = ['npm install', 'pip install', 'dotnet restore', 'nuget restore', 
                     '--version', 'config --list', 'config list', 'ls', 'dir', 'tree',
                     'export ', '$env:']
    
    unsafe_keywords = ['rm ', 'del ', 'Remove-Item', 'sudo', 'chmod', 'chown',
                       'curl ', 'wget', 'Invoke-WebRequest', 'msbuild', 'dotnet build',
                       'npm run build', 'DROP', 'DELETE', 'UPDATE', 'INSERT']
    
    os.chdir(repo_dir)
    
    for cmd in commands:
        # Classify command
        is_safe = any(keyword in cmd for keyword in safe_keywords)
        is_unsafe = any(keyword in cmd for keyword in unsafe_keywords)
        
        if is_unsafe or not is_safe:
            # Skip unsafe or unknown commands
            reason = 'unsafe operation detected' if is_unsafe else 'command not in safe list'
            setup_commands_skipped.append({'command': cmd, 'reason': reason})
            if DEBUG:
                print(f'[debug][task-execute-readme] skipping unsafe command: {cmd}')
        else:
            # Execute safe command
            if DEBUG:
                print(f'[debug][task-execute-readme] executing safe setup command: {cmd}')
            
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                exit_code = result.returncode
                
                if DEBUG:
                    print(f'[debug][task-execute-readme] command exit code: {exit_code}')
                
                setup_commands_executed.append({
                    'command': cmd,
                    'exit_code': exit_code,
                    'stdout': result.stdout[:500] if result.stdout else '',
                    'stderr': result.stderr[:500] if result.stderr else ''
                })
            except subprocess.TimeoutExpired:
                setup_commands_skipped.append({'command': cmd, 'reason': 'timeout (>30s)'})
                if DEBUG:
                    print(f'[debug][task-execute-readme] command timed out: {cmd}')
            except Exception as e:
                setup_commands_skipped.append({'command': cmd, 'reason': f'execution error: {str(e)}'})
    
    if DEBUG:
        print(f'[debug][task-execute-readme] executed {len(setup_commands_executed)} safe commands, skipped {len(setup_commands_skipped)} unsafe commands')

status = 'SUCCESS' if readme_filename else 'FAIL'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Update tracking files
os.chdir(r'C:\Users\sacheu\source\build_repo_v3')

with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if repo_name in line:
        parts = line.split('|')
        if len(parts) >= 4 and '[ ]' in parts[3]:
            parts[3] = parts[3].replace('[ ]', '[x]', 1)
            lines[i] = '|'.join(parts)
            break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Append to results files
with open('results/repo-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | task-execute-readme | {status} | {timestamp} |\n')
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},task-execute-readme,{status},{timestamp}\n')

if DEBUG:
    print(f'[debug][task-execute-readme] END repo_directory="{repo_dir}" status={status} readme_found={readme_filename} commands_executed={len(setup_commands_executed)}')

print(f'[run10][execute-readme] readme_file="{readme_filename}" commands_executed={len(setup_commands_executed)} commands_skipped={len(setup_commands_skipped)}')
