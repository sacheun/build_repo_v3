import json
from datetime import datetime

# Load solutions from output/solutions.json
with open('output/solutions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    solutions = data['solutions']

solution_count = len(solutions)
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Create solution-progress.md
progress_content = f"""# Run 9 - Solution Task Progress - {timestamp}

| Solution | task-restore-solution | task-build-solution |
|----------|----------------------|---------------------|
"""

for sln_path in solutions:
    sln_name = sln_path.split('\\')[-1].replace('.sln', '')
    progress_content += f'| {sln_name} | [ ] | [ ] |\n'

with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.write(progress_content)

# Create solution-results.md
results_md_content = f"""# Run 9 - Solution Task Results - {timestamp}

| Solution | Task | Status | Timestamp |
|----------|------|--------|-----------|
"""

with open('results/solution-results.md', 'w', encoding='utf-8') as f:
    f.write(results_md_content)

# Create solution-results.csv
with open('results/solution-results.csv', 'w', encoding='utf-8') as f:
    f.write('Solution,Task,Status,Timestamp\n')

print(f'[run9][init] solution tracking initialized with {solution_count} solutions and 2 task columns')
