"""
Initialize repository tracking files.
Reads repositories.txt and creates progress/results files.
"""

import os
from datetime import datetime

# Ensure directories exist
os.makedirs('results', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Read repository URLs
repositories_file = '.copilot/prompts/repositories.txt'
repo_urls = []
with open(repositories_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            repo_urls.append(line)

# Extract repo names
repo_names = []
for url in repo_urls:
    repo_name = url.rstrip('/').split('/')[-1]
    repo_names.append(repo_name)

# Create repo-progress.md
repo_progress_md = 'results/repo-progress.md'
with open(repo_progress_md, 'w') as f:
    f.write("# Repository Progress - Run 13\n\n")
    f.write("| Repository | task-clone-repo | task-execute-readme | task-find-solutions | task-process-solutions |\n")
    f.write("|------------|-----------------|---------------------|---------------------|------------------------|\n")
    for repo_name in repo_names:
        f.write(f"| {repo_name} | [ ] | [ ] | [ ] | [ ] |\n")

print(f"Created {repo_progress_md} with {len(repo_names)} repositories")

# Create repo-results.csv
repo_results_csv = 'results/repo-results.csv'
with open(repo_results_csv, 'w') as f:
    f.write("Repository,Task,Result,Timestamp\n")

print(f"Created {repo_results_csv}")

# Create solution-progress.md
solution_progress_md = 'results/solution-progress.md'
with open(solution_progress_md, 'w') as f:
    f.write("# Solution Progress - Run 13\n\n")
    f.write("| Repository | Solution | task-restore-solution | task-build-solution | task-collect-knowledge-base |\n")
    f.write("|------------|----------|----------------------|---------------------|-----------------------------|\n")

print(f"Created {solution_progress_md}")

# Create solution-results.csv
solution_results_csv = 'results/solution-results.csv'
with open(solution_results_csv, 'w') as f:
    f.write("Repository,Solution,Task,Result,Timestamp\n")

print(f"Created {solution_results_csv}")

print("Initialization complete!")
