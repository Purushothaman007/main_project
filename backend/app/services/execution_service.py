import os
from app.core.config import settings
from app.core.logging_config import logger
from app.models.language_config import get_language_config, LanguageConfig
from app.schemas.execute import ExecutionRequest, ExecutionResponse, ExecutionStatus
from app.services.docker_service import docker_service
from app.utils.id_generator import generate_execution_id
from app.utils.workspace import create_temp_workspace

class ExecutionService:
    def execute_code(self, request: ExecutionRequest) -> ExecutionResponse:
        exec_id = generate_execution_id()
        lang_key = request.language.lower()
        lang_config = get_language_config(lang_key)

        if not lang_config:
            return ExecutionResponse(
                success=False,
                language=request.language,
                stdout="",
                stderr=f"Unsupported language: {request.language}",
                exit_code=-1,
                execution_time_ms=0,
                status=ExecutionStatus.SYSTEM_ERROR,
                execution_id=exec_id
            )

        # Validate source code size
        source_bytes = len(request.code.encode('utf-8'))
        if source_bytes > settings.MAX_SOURCE_SIZE_BYTES:
            return ExecutionResponse(
                success=False,
                language=request.language,
                stdout="",
                stderr=f"Source code size ({source_bytes} bytes) exceeds limit of {settings.MAX_SOURCE_SIZE_BYTES} bytes.",
                exit_code=-1,
                execution_time_ms=0,
                status=ExecutionStatus.SYSTEM_ERROR,
                execution_id=exec_id
            )

        # Validate stdin size
        stdin_str = request.stdin or ""
        stdin_bytes = len(stdin_str.encode('utf-8'))
        if stdin_bytes > settings.MAX_STDIN_SIZE_BYTES:
            return ExecutionResponse(
                success=False,
                language=request.language,
                stdout="",
                stderr=f"Stdin size ({stdin_bytes} bytes) exceeds limit of {settings.MAX_STDIN_SIZE_BYTES} bytes.",
                exit_code=-1,
                execution_time_ms=0,
                status=ExecutionStatus.SYSTEM_ERROR,
                execution_id=exec_id
            )

        logger.info(f"[{exec_id}] Starting execution for language '{lang_key}'")

        with create_temp_workspace() as workspace_dir:
            # Write source code file
            source_file_path = os.path.join(workspace_dir, lang_config.source_file)
            with open(source_file_path, "w", encoding="utf-8") as f:
                f.write(request.code)

            # Compilation step (if defined for language)
            if lang_config.compile:
                compile_timed_out, compile_exit, compile_stdout, compile_stderr, _, compile_out_exceeded = (
                    docker_service.execute_in_container(
                        image=lang_config.image,
                        command=lang_config.compile,
                        workspace_dir=workspace_dir,
                        stdin="",
                        timeout_sec=settings.MAX_COMPILATION_TIME_SEC,
                        max_output_bytes=settings.MAX_STDOUT_SIZE_BYTES
                    )
                )

                if compile_timed_out:
                    return ExecutionResponse(
                        success=False,
                        language=request.language,
                        stdout=compile_stdout,
                        stderr=f"Compilation timed out after {settings.MAX_COMPILATION_TIME_SEC} seconds.",
                        exit_code=-1,
                        execution_time_ms=settings.MAX_COMPILATION_TIME_SEC * 1000,
                        status=ExecutionStatus.COMPILATION_ERROR,
                        execution_id=exec_id
                    )

                if compile_exit != 0:
                    return ExecutionResponse(
                        success=False,
                        language=request.language,
                        stdout=compile_stdout,
                        stderr=compile_stderr,
                        exit_code=compile_exit,
                        execution_time_ms=0,
                        status=ExecutionStatus.COMPILATION_ERROR,
                        execution_id=exec_id
                    )

            # Execution step
            timed_out, exit_code, stdout_str, stderr_str, duration_ms, out_exceeded = (
                docker_service.execute_in_container(
                    image=lang_config.image,
                    command=lang_config.run,
                    workspace_dir=workspace_dir,
                    stdin=stdin_str,
                    timeout_sec=settings.MAX_EXECUTION_TIME_SEC,
                    max_output_bytes=settings.MAX_STDOUT_SIZE_BYTES
                )
            )

            if timed_out:
                logger.info(f"[{exec_id}] Execution timed out after {settings.MAX_EXECUTION_TIME_SEC}s")
                return ExecutionResponse(
                    success=False,
                    language=request.language,
                    stdout=stdout_str,
                    stderr="Execution timed out.",
                    exit_code=-1,
                    execution_time_ms=settings.MAX_EXECUTION_TIME_SEC * 1000,
                    status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
                    execution_id=exec_id
                )

            if out_exceeded:
                logger.info(f"[{exec_id}] Output limit exceeded")
                return ExecutionResponse(
                    success=False,
                    language=request.language,
                    stdout=stdout_str,
                    stderr=stderr_str + "\n[Output limit exceeded]",
                    exit_code=exit_code,
                    execution_time_ms=duration_ms,
                    status=ExecutionStatus.OUTPUT_LIMIT_EXCEEDED,
                    execution_id=exec_id
                )

            if exit_code != 0:
                logger.info(f"[{exec_id}] Process exited non-zero ({exit_code})")
                # Exit code 137 indicates SIGKILL, commonly triggered by Linux OOM killer when memory limit is breached
                status_val = ExecutionStatus.MEMORY_LIMIT_EXCEEDED if exit_code == 137 else ExecutionStatus.RUNTIME_ERROR
                stderr_msg = stderr_str + ("\n[Memory limit exceeded]" if exit_code == 137 else "")
                return ExecutionResponse(
                    success=False,
                    language=request.language,
                    stdout=stdout_str,
                    stderr=stderr_msg,
                    exit_code=exit_code,
                    execution_time_ms=duration_ms,
                    status=status_val,
                    execution_id=exec_id
                )

            logger.info(f"[{exec_id}] Execution completed successfully in {duration_ms}ms")
            return ExecutionResponse(
                success=True,
                language=request.language,
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=0,
                execution_time_ms=duration_ms,
                status=ExecutionStatus.COMPLETED,
                execution_id=exec_id
            )

execution_service = ExecutionService()
