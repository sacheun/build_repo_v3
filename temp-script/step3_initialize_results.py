import os
from pathlib import Path

os.environ['DEBUG'] = '1'

print("Initializing results files...")

# Create repo-results.md
repo_results_md = Path("results/repo-results.md")
with open(repo_results_md, 'w', encoding='utf-8') as f:
    f.write("| Timestamp | Repository | Task | Status | Symbol |\n")
    f.write("|---|---|---|---|---|\n")

print(f"Created: {repo_results_md}")

# Create repo-results.csv
repo_results_csv = Path("results/repo-results.csv")
with open(repo_results_csv, 'w', encoding='utf-8') as f:
    f.write("Timestamp,Repository,Task,Status,Symbol\n")

print(f"Created: {repo_results_csv}")

# Create solution-results.md
solution_results_md = Path("results/solution-results.md")
with open(solution_results_md, 'w', encoding='utf-8') as f:
    f.write("| Timestamp | Repository | Solution | Task | Status | Symbol |\n")
    f.write("|---|---|---|---|---|---|\n")

print(f"Created: {solution_results_md}")

# Create solution-results.csv
solution_results_csv = Path("results/solution-results.csv")
with open(solution_results_csv, 'w', encoding='utf-8') as f:
    f.write("Timestamp,Repository,Solution,Task,Status,Symbol\n")

print(f"Created: {solution_results_csv}")

print("\nResults files initialized successfully!")
