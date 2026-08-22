# Execution Flow Document

## Detailed Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant FE as React Frontend
    participant API as FastAPI Router
    participant Service as ExecutionService
    participant DockerSvc as DockerService
    participant Docker as Docker Container

    Student->>FE: Select Language, Code & Stdin -> Click Run
    FE->>API: POST /api/v1/execute (JSON)
    API->>Service: execute_code(ExecutionRequest)
    Service->>Service: Validate source code size (<100KB) & stdin size (<100KB)
    Service->>Service: Create temporary host directory (/tmp/code_exec_xxxx)
    Service->>Service: Write source file (main.py / Main.java / main.cpp)
    
    alt Language requires compilation (Java / C++)
        Service->>DockerSvc: execute_in_container(compile command)
        DockerSvc->>Docker: Spawn sandbox container & run compiler
        Docker-->>DockerSvc: Compiler logs & exit code
        alt Compile Failed (exit code != 0)
            DockerSvc-->>Service: Compilation Error
            Service-->>FE: Return status: COMPILATION_ERROR
        end
    end

    Service->>DockerSvc: execute_in_container(run command + stdin)
    DockerSvc->>Docker: Spawn fresh container (net disabled, 256MB RAM, 1 CPU, 64 PIDs)
    DockerSvc->>Docker: Stream stdin via raw socket
    Docker-->>DockerSvc: Execute code & capture stdout / stderr
    
    alt Timeout breached (> 5s)
        DockerSvc->>Docker: Kill & force remove container
        Service-->>FE: Return status: TIME_LIMIT_EXCEEDED
    else OOM killer triggered (Exit Code 137)
        Service-->>FE: Return status: MEMORY_LIMIT_EXCEEDED
    else Exit code != 0
        Service-->>FE: Return status: RUNTIME_ERROR
    else Execution Success
        Service-->>FE: Return status: COMPLETED
    end

    opt Clean Up (Guaranteed via try...finally)
        DockerSvc->>Docker: Remove container
        Service->>Service: Delete temporary directory
    end
```

## Status Classification Matrix

| Status | Trigger Condition | Output Returned |
| :--- | :--- | :--- |
| `COMPLETED` | Exit Code `0`, no limits breached | Captured `stdout`, empty `stderr` |
| `COMPILATION_ERROR` | Compiler (`javac` / `g++`) exit code != 0 | Compiler error logs (`stderr`) |
| `RUNTIME_ERROR` | Runtime crash, unhandled exception, segfault | Exception traceback / error log |
| `TIME_LIMIT_EXCEEDED` | Process wall-clock execution > 5s | Truncated logs prior to kill |
| `MEMORY_LIMIT_EXCEEDED` | RAM allocation > 256MB (Exit code 137) | OOM notice & stderr logs |
| `OUTPUT_LIMIT_EXCEEDED` | `stdout` / `stderr` > 1MB | Truncated log block + cap notice |
| `SYSTEM_ERROR` | Invalid language or source/stdin size breach | Generic sanitized system error |
