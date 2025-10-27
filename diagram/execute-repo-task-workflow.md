# Execute-Repo-Task Workflow Diagram

This diagram shows the workflow for the `@execute-repo-task` prompt, including task execution order, conditions, and scriptable vs non-scriptable tasks.

```mermaid
flowchart TD
    Start([Start @execute-repo-task]) --> Init[Initialize<br/>Parameters]
    
    Init --> Loop{Continuous Loop}
    
    Loop --> ReadMaster[Read Master<br/>Checklist]
    
    ReadMaster --> CheckAllRepos{All repos<br/>complete?}
    CheckAllRepos -->|Yes| AllComplete[ALL_COMPLETE<br/>Exit & Return Summary]
    CheckAllRepos -->|No| FindFirstRepo[Find next<br/>uncompleted repo]
    
    FindFirstRepo --> CloneRepo[1. Clone Repo]
    
    %% Sequential Task Execution
    CloneRepo --> SearchReadme[2. Search README]
    
    %% Conditional Tasks
    SearchReadme --> CheckReadmeExists{3. Scan README - CONDITIONAL<br/>README exists?}
    CheckReadmeExists -->|Yes| ScanReadme[3. Scan README<br/>AI Reasoning]
    CheckReadmeExists -->|No| SkipScan[SKIP<br/>No README]
    
    ScanReadme --> CheckCommandsExists{4. Execute Commands - CONDITIONAL<br/>Commands found?}
    SkipScan --> CheckCommandsExists
    CheckCommandsExists -->|Yes| ExecuteReadme[4. Execute Commands<br/>AI Reasoning]
    CheckCommandsExists -->|No| SkipExecute[SKIP<br/>No commands]
    
    %% Continue with remaining mandatory tasks
    ExecuteReadme --> FindSolutions[5. Find Solutions]
    SkipExecute --> FindSolutions
    FindSolutions --> GenerateChecklists[6. Generate Solution Checklists]
    
    %% Task Results
    GenerateChecklists --> TaskResult{Success?}
    
    TaskResult -->|Success| UpdateChecklist[Update Checklist<br/>& Variables]
    TaskResult -->|Fail| TaskFailed[FAIL<br/>Exit & Return Summary]
    
    UpdateChecklist --> CheckRepoComplete{Repo<br/>complete?}
    CheckRepoComplete -->|Yes| MarkRepoComplete[Mark Repo Complete<br/>Continue to next repo]
    CheckRepoComplete -->|No| NextTask[Continue to next task]
    
    MarkRepoComplete --> Loop
    NextTask --> Loop
    
    %% Exit States
    TaskFailed --> End
    AllComplete --> End
    
    %% High Contrast Styling for Presentations
    classDef mandatory fill:#ffffff,stroke:#28a745,stroke-width:3px,color:#000000
    classDef conditional fill:#ffffff,stroke:#ffc107,stroke-width:3px,color:#000000
    classDef scriptable fill:#cfe2ff,stroke:#007bff,stroke-width:3px,color:#000000
    classDef aiReasoning fill:#f8d7da,stroke:#dc3545,stroke-width:3px,color:#000000
    classDef decision fill:#ffffff,stroke:#6c757d,stroke-width:3px,color:#000000
    classDef process fill:#ffffff,stroke:#17a2b8,stroke-width:2px,color:#000000
    classDef terminal fill:#ffffff,stroke:#343a40,stroke-width:3px,color:#000000
    classDef skip fill:#ffffff,stroke:#6c757d,stroke-width:2px,color:#000000
    
    class CloneRepo,SearchReadme,FindSolutions,GenerateChecklists mandatory
    class CheckReadmeExists,CheckCommandsExists conditional
    class CloneRepo,SearchReadme,FindSolutions,GenerateChecklists scriptable
    class ScanReadme,ExecuteReadme aiReasoning
    class CheckAllRepos,TaskResult,CheckRepoComplete decision
    class Init,ReadMaster,FindFirstRepo,UpdateChecklist,MarkRepoComplete,NextTask process
    class Start,End,AllComplete,TaskFailed terminal
    class SkipScan,SkipExecute skip
```

## Task Execution Overview

### Mandatory Tasks (Always Execute in Order)
1. **Clone Repository** [SCRIPTABLE] - Generates Python script
2. **Search README** [SCRIPTABLE] - Generates Python script  
5. **Find Solutions** [SCRIPTABLE] - Generates Python script
6. **Generate Solution Checklists** [SCRIPTABLE] - Generates Python script

### Conditional Tasks (Execute Based on Conditions)
3. **Scan README** [CONDITIONAL] - Requires AI reasoning
   - **Condition:** README content exists 
   - **If TRUE:** Execute with AI reasoning
   - **If FALSE:** Skip task

4. **Execute Commands** [CONDITIONAL] - Requires AI reasoning
   - **Condition:** Commands found in README
   - **If TRUE:** Execute with AI reasoning  
   - **If FALSE:** Skip task

## Key Workflow Features

- **Sequential Execution:** Tasks run in strict order (1→2→3→4→5→6)
- **Autonomous Loop:** Processes all repos continuously  
- **Conditional Logic:** Smart skipping based on content availability
- **Error Handling:** Stops on failure or missing dependencies
- **Resumable:** Can restart from any checkpoint

## Color Legend
- 🟢 **Green:** Mandatory scriptable tasks
- 🟡 **Yellow:** Conditional decision points  
- 🔵 **Blue:** Scriptable automation tasks
- 🔴 **Red:** AI reasoning required tasks
- ⚪ **Gray:** Process steps and decisions