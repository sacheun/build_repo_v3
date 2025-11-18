# Generate HTML Report from CSV Results

## Objective
Generate a **single HTML file** containing two tables from CSV execution results:
1. **Repository-level table** from `repo_result.csv`
2. **Solution-level table** from `solution_result.csv`

Both tables will be combined into one HTML file: `results/execution_results.html`

## Instructions

### Task 1: Generate Repository-Level HTML Table

**Input File:** `results/repo_result.csv`

**Steps:**
1. Read `repo_result.csv` (format: `repo,task name,status`)
2. **Skip the header row** (first row contains column names, not data)
3. Extract all unique task names from the CSV
4. Create an HTML table with:
   - **First column:** Repository name
   - **Subsequent columns:** One column per unique task name (sorted alphabetically)
   - **Cell values:** The `status` value for that repo + task combination
5. Return HTML table string (not full page)

**Table Structure:**
```html
<table border="1">
  <thead>
    <tr>
      <th>Repository</th>
      <th>Task 1 Name</th>
      <th>Task 2 Name</th>
      <!-- ... more task columns ... -->
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>repo_name_1</td>
      <td>status_value</td>
      <td>status_value</td>
      <!-- ... more status cells ... -->
    </tr>
    <!-- ... more repository rows ... -->
  </tbody>
</table>
```

**Styling Requirements:**
- Add CSS styling for better readability
- Color-code status values:
  - SUCCESS: green background
  - FAILED: red background
  - SKIPPED: yellow background
  - NOT_FOUND: orange background
  - NOT_EXECUTED: gray background
- Add table borders and padding
- Make header row bold with dark background

---

### Task 2: Generate Solution-Level HTML Table

**Input File:** `results/solution_result.csv`

**Steps:**
1. Read `solution_result.csv` (format: `repo,solution,task name,status`)
2. **Skip the header row** (first row contains column names, not data)
3. Extract all unique task names from the CSV
4. Create an HTML table with:
   - **First column:** Repository name
   - **Second column:** Solution name
   - **Subsequent columns:** One column per unique task name (sorted alphabetically)
   - **Cell values:** The `status` value for that repo + solution + task combination
5. Return HTML table string (not full page)

---

### Task 3: Combine Tables into Single HTML File

**Steps:**
1. Generate repository-level table from Task 1
2. Generate solution-level table from Task 2
3. Create complete HTML page with:
   - HTML structure (head, body)
   - CSS styling
   - Page title: "Build Repository Execution Results"
   - Timestamp
   - Repository table with heading "Repository-Level Execution Results"
   - Solution table with heading "Solution-Level Execution Results"
4. Save to `results/execution_results.html`

**Table Structure:**
```html
<table border="1">
  <thead>
    <tr>
      <th>Repository</th>
      <th>Solution</th>
      <th>Task 1 Name</th>
      <th>Task 2 Name</th>
      <!-- ... more task columns ... -->
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>repo_name</td>
      <td>solution_name.sln</td>
      <td>status_value</td>
      <td>status_value</td>
      <!-- ... more status cells ... -->
    </tr>
    <!-- ... more solution rows ... -->
  </tbody>
</table>
```

**Styling Requirements:**
- Same color-coding as Task 1
- Group rows by repository (add visual separator or alternating row colors)
- Make table responsive
- Add hover effects on rows
- Include title and timestamp

---

## Implementation Details

### Python Script Template

```python
#!/usr/bin/env python3
"""
Generate HTML reports from CSV execution results
"""

import csv
from pathlib import Path
from datetime import datetime

def get_status_color(status):
    """Return CSS class for status value"""
    colors = {
        'SUCCESS': 'status-success',
        'FAILED': 'status-failed',
        'SKIPPED': 'status-skipped',
        'NOT_FOUND': 'status-not-found',
        'NOT_EXECUTED': 'status-not-executed'
    }
    return colors.get(status, 'status-unknown')

def generate_css():
    """Generate CSS styling for tables"""
    return '''
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0078d4;
            padding-bottom: 10px;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        th {
            background-color: #0078d4;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            position: sticky;
            top: 0;
        }
        td {
            padding: 10px;
            border: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f0f0f0;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .status-success {
            background-color: #d4edda;
            color: #155724;
            font-weight: bold;
        }
        .status-failed {
            background-color: #f8d7da;
            color: #721c24;
            font-weight: bold;
        }
        .status-skipped {
            background-color: #fff3cd;
            color: #856404;
        }
        .status-not-found {
            background-color: #ffeaa7;
            color: #d63031;
        }
        .status-not-executed {
            background-color: #e9ecef;
            color: #6c757d;
        }
        .status-unknown {
            background-color: #f8f9fa;
            color: #333;
        }
        .repo-name {
            font-weight: bold;
            color: #0078d4;
        }
        .solution-name {
            font-family: 'Courier New', monospace;
            color: #333;
        }
    </style>
    '''

def generate_repo_html(csv_path):
    """Generate HTML table for repo_result.csv (returns HTML string)"""
    # Read CSV and collect data
    repos = {}
    all_tasks = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            if len(row) >= 3:
                repo, task, status = row[0], row[1], row[2]
                all_tasks.add(task)
                if repo not in repos:
                    repos[repo] = {}
                repos[repo][task] = status
    
    # Sort tasks alphabetically
    sorted_tasks = sorted(all_tasks)
    
    # Generate HTML table (not full page)
    html = []
    html.append('<h2>Repository-Level Execution Results</h2>')
    html.append('<table>')
    
    # Header
    html.append('<thead><tr>')
    html.append('<th>Repository</th>')
    for task in sorted_tasks:
        html.append(f'<th>{task}</th>')
    html.append('</tr></thead>')
    
    # Body
    html.append('<tbody>')
    for repo in sorted(repos.keys()):
        html.append('<tr>')
        html.append(f'<td class="repo-name">{repo}</td>')
        for task in sorted_tasks:
            status = repos[repo].get(task, '')
            css_class = get_status_color(status)
            html.append(f'<td class="{css_class}">{status}</td>')
        html.append('</tr>')
    html.append('</tbody>')
    html.append('</table>')
    
    print(f'  Repositories: {len(repos)}')
    print(f'  Task columns: {len(sorted_tasks)}')
    
    return '\n'.join(html)

def generate_solution_html(csv_path):
    """Generate HTML table for solution_result.csv (returns HTML string)"""
    # Read CSV and collect data
    solutions = []  # List of (repo, solution, {task: status})
    all_tasks = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            if len(row) >= 4:
                repo, solution, task, status = row[0], row[1], row[2], row[3]
                all_tasks.add(task)
                
                # Find or create solution entry
                found = False
                for sol_data in solutions:
                    if sol_data[0] == repo and sol_data[1] == solution:
                        sol_data[2][task] = status
                        found = True
                        break
                
                if not found:
                    solutions.append([repo, solution, {task: status}])
    
    # Sort tasks alphabetically
    sorted_tasks = sorted(all_tasks)
    
    # Generate HTML table (not full page)
    html = []
    html.append('<h2>Solution-Level Execution Results</h2>')
    html.append('<table>')
    
    # Header
    html.append('<thead><tr>')
    html.append('<th>Repository</th>')
    html.append('<th>Solution</th>')
    for task in sorted_tasks:
        html.append(f'<th>{task}</th>')
    html.append('</tr></thead>')
    
    # Body
    html.append('<tbody>')
    for repo, solution, tasks in solutions:
        html.append('<tr>')
        html.append(f'<td class="repo-name">{repo}</td>')
        html.append(f'<td class="solution-name">{solution}</td>')
        for task in sorted_tasks:
            status = tasks.get(task, '')
            css_class = get_status_color(status)
            html.append(f'<td class="{css_class}">{status}</td>')
        html.append('</tr>')
    html.append('</tbody>')
    html.append('</table>')
    
    print(f'  Solutions: {len(solutions)}')
    print(f'  Task columns: {len(sorted_tasks)}')
    
    return '\n'.join(html)

if __name__ == '__main__':
    # Generate combined report
    print('\n========================================')
    print('Generating HTML Report')
    print('========================================\n')
    
    # Task 1: Repository-level table
    print('[Task 1] Repository-level table...')
    repo_table = generate_repo_html('results/repo_result.csv')
    
    # Task 2: Solution-level table
    print('\n[Task 2] Solution-level table...')
    solution_table = generate_solution_html('results/solution_result.csv')
    
    # Task 3: Combine into single HTML file
    html = ['<!DOCTYPE html>']
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('<meta charset="UTF-8">')
    html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('<title>Execution Results</title>')
    html.append(generate_css())
    html.append('</head>')
    html.append('<body>')
    html.append('<h1>Build Repository Execution Results</h1>')
    html.append(f'<div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>')
    html.append(repo_table)
    html.append('<br>')
    html.append(solution_table)
    html.append('</body>')
    html.append('</html>')
    
    # Write combined report
    output_path = 'results/execution_results.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f'\n✓ Generated: {output_path}')
    print('\n========================================')
    print('HTML Report Generated Successfully!')
    print('========================================\n')
```

---

## Expected Output

### File: results/execution_results.html
A single HTML file containing:
- **Page title:** "Build Repository Execution Results"
- **Timestamp:** When the report was generated
- **Table 1:** Repository-level execution results
  - Compact table showing repository-level execution status
  - One row per repository
  - Color-coded status cells
- **Table 2:** Solution-level execution results
  - Detailed table showing all solution execution statuses
  - One row per solution
  - Grouped by repository
  - Color-coded status cells
- **Responsive design** with sticky headers for easy scrolling

---

## Usage

1. Save the Python script to: `temp-script/generate_html_reports.py`
2. Run the script:
   ```bash
   python temp-script/generate_html_reports.py
   ```
3. Open the generated HTML file:
   - `results/execution_results.html`

---

## Customization Options

### Adjust Colors
Modify the CSS in `generate_css()` function to change status colors.

### Add Statistics
Add summary statistics at the top of each HTML file (total repos, total solutions, success rate, etc.).

### Export Formats
Extend script to also generate:
- JSON export
- Excel export
- PDF report (using libraries like `reportlab` or `weasyprint`)

### Filtering
Add command-line arguments to filter by:
- Repository name
- Status (e.g., only show FAILED)
- Task name

---

## Success Criteria

✅ Single HTML file generated without errors  
✅ CSV header rows properly skipped (no "repo" row in output)  
✅ Both tables included in same file  
✅ All repositories/solutions included  
✅ All unique tasks appear as columns  
✅ Status values correctly mapped to cells  
✅ Color coding applied and readable  
✅ Tables are responsive and well-formatted  
✅ Timestamp included in report  

---

*End of Prompt*
