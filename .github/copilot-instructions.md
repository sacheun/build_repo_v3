**Important**

1. Do not generate a single comprehensive script to process all tasks. The workflow includes both scriptable and non-scriptable tasks, and each task must be handled according to its label.
2. For tasks labelled “skippable,” you are allowed to generate scripts to complete the task. For tasks labelled “non-scriptable,” you must not generate scripts. Use AI-based structured reasoning to accomplish non-scriptable tasks instead.
3. Execute the tasks in the markdown file one task at a time. Do not skip any task. Do not group scriptable and non scriptable tasks in 1 script.
4. Follow the command list exactly as defined in the instruction markdown files located in the repository.
5. For each conditional task, verify its condition. If the condition is met, execute the task.
6. After completing a task, you must update the designated repository markdown file by changing the task status from “[ ]” to “[x]” to reflect completion.
7. For scriptable task, generate Python code that runs on Windows 11 using UTF-8 encoding. Ensure subprocess calls use `encoding='utf-8'` and `errors='ignore'`. Avoid using unescaped backslashes in file paths.