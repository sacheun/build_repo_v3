import os
from pathlib import Path

os.environ['DEBUG'] = '1'

print("[debug][init-results] START initializing results files")

# Create repo-results.md
repo_results_md = Path("results/repo-results.md")
with open(repo_results_md, 'w', encoding='utf-8') as f:
    f.write("| Timestamp | Repository | Task | Status | Symbol |\n")
    f.write("|-----------|------------|------|--------|--------|\n")

# Create repo-results.csv
repo_results_csv = Path("results/repo-results.csv")
with open(repo_results_csv, 'w', encoding='utf-8') as f:
    f.write("Timestamp,Repository,Task,Status,Symbol\n")

# Create solution-results.md
solution_results_md = Path("results/solution-results.md")
with open(solution_results_md, 'w', encoding='utf-8') as f:
    f.write("| Timestamp | Repository | Solution | Task | Status | Symbol |\n")
    f.write("|-----------|------------|----------|------|--------|--------|\n")

# Create solution-results.csv
solution_results_csv = Path("results/solution-results.csv")
with open(solution_results_csv, 'w', encoding='utf-8') as f:
    f.write("Timestamp,Repository,Solution,Task,Status,Symbol\n")

print(f"[debug][init-results] created {repo_results_md}")
print(f"[debug][init-results] created {repo_results_csv}")
print(f"[debug][init-results] created {solution_results_md}")
print(f"[debug][init-results] created {solution_results_csv}")
print("[debug][init-results] EXIT status='SUCCESS'")
