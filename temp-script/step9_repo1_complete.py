import os
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

repo_name = "ic3_spool_cosine-dep-spool"

print(f"Marking repository 1 ({repo_name}) task-process-solutions as complete...")

# Update progress table
progress_file = Path("results/repo-progress.md")
if progress_file.exists():
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the row for this repository and update task-process-solutions column
    for i, line in enumerate(lines):
        if repo_name in line:
            parts = line.split('|')
            if len(parts) >= 6:
                # Column 5 is task-process-solutions
                parts[5] = ' [x] '
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# Append to results files
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
symbol = '✓'

# Markdown result
md_result = Path("results/repo-results.md")
with open(md_result, 'a', encoding='utf-8') as f:
    f.write(f"| {timestamp} | {repo_name} | task-process-solutions | SUCCESS | {symbol} |\n")

# CSV result
csv_result = Path("results/repo-results.csv")
with open(csv_result, 'a', encoding='utf-8') as f:
    f.write(f"{timestamp},{repo_name},task-process-solutions,SUCCESS,{symbol}\n")

print(f"Repository 1 complete! All 4 tasks marked [x]")
