import os
from docker.errors import DockerException
from app.core.config import settings
from app.core.logging_config import logger
from app.models.language_config import get_language_config, LanguageConfig, COMPILE_FAILURE_EXIT_CODE
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

        try:
            docker_service.client  # Eagerly check Docker is reachable before touching the workspace
        except DockerException as e:
            logger.error(f"[{exec_id}] Docker daemon is unavailable: {e}")
            return ExecutionResponse(
                success=False,
                language=request.language,
                stdout="",
                stderr="Docker daemon is unavailable. Please ensure Docker Desktop is running.",
                exit_code=-1,
                execution_time_ms=0,
                status=ExecutionStatus.SYSTEM_ERROR,
                execution_id=exec_id
            )

        # ================================================================
        # WARM POOL PATH — zero cold-start cost
        # Attempt to acquire a pre-warmed container. Files are uploaded
        # via put_archive; commands run via docker exec. The container is
        # destroyed and asynchronously replaced after every execution.
        # Falls back to the on-demand paths below if the pool is empty.
        # ================================================================
        warm_response = self._try_warm_execution(
            exec_id=exec_id,
            request=request,
            lang_config=lang_config,
            stdin_str=stdin_str,
        )
        if warm_response is not None:
            return warm_response

        # ================================================================
        # FALLBACK: on-demand container paths (pool empty / pool miss)
        # ================================================================
        with create_temp_workspace() as workspace_dir:
            # Write source code file to host workspace (volume-mounted)
            source_file_path = os.path.join(workspace_dir, lang_config.source_file)
            with open(source_file_path, "w", encoding="utf-8") as f:
                f.write(request.code)

            # ----------------------------------------------------------------
            # Fast path: compile + run inside a SINGLE container (Java, C++)
            # The combined_run script exits with COMPILE_FAILURE_EXIT_CODE (64)
            # on compile failure so we can still report COMPILATION_ERROR.
            # ----------------------------------------------------------------
            if lang_config.combined_run:
                combined_timeout = settings.MAX_COMPILATION_TIME_SEC + settings.MAX_EXECUTION_TIME_SEC
                timed_out, exit_code, stdout_str, stderr_str, duration_ms, out_exceeded = (
                    docker_service.execute_in_container(
                        image=lang_config.image,
                        command=lang_config.combined_run,
                        workspace_dir=workspace_dir,
                        stdin=stdin_str,
                        timeout_sec=combined_timeout,
                        max_output_bytes=settings.MAX_STDOUT_SIZE_BYTES
                    )
                )

                if timed_out:
                    logger.info(f"[{exec_id}] Execution timed out after {combined_timeout}s")
                    return ExecutionResponse(
                        success=False,
                        language=request.language,
                        stdout=stdout_str,
                        stderr="Execution timed out.",
                        exit_code=-1,
                        execution_time_ms=combined_timeout * 1000,
                        status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
                        execution_id=exec_id
                    )

                if exit_code == COMPILE_FAILURE_EXIT_CODE:
                    logger.info(f"[{exec_id}] Compilation failed (single-container path)")
                    clean_stdout = stdout_str.replace("__COMPILE_ERROR__\n", "").replace("__COMPILE_ERROR__", "")
                    return ExecutionResponse(
                        success=False,
                        language=request.language,
                        stdout=clean_stdout,
                        stderr=stderr_str,
                        exit_code=exit_code,
                        execution_time_ms=duration_ms,
                        status=ExecutionStatus.COMPILATION_ERROR,
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

                logger.info(f"[{exec_id}] Execution completed successfully in {duration_ms}ms (single-container)")
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

            # ----------------------------------------------------------------
            # Standard path: separate containers for compile and run
            # Used for languages without a combined_run (currently: Python)
            # ----------------------------------------------------------------

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

    # ----------------------------------------------------------------
    # Warm pool execution — private helper
    # ----------------------------------------------------------------

    def _try_warm_execution(
        self,
        exec_id: str,
        request: ExecutionRequest,
        lang_config: LanguageConfig,
        stdin_str: str,
    ):
        """
        Try to execute using a pre-warmed container from the pool.

        Returns an ExecutionResponse if execution succeeded or failed cleanly,
        or None if no warm container was available (caller should fall back).

        Strategy:
          - Acquire a warm container (non-blocking).
          - Upload source file + .stdin_input via put_archive (in-memory tar).
          - For compiled languages: exec compile step, check exit code.
          - exec run step, check exit code.
          - Always call release_and_replace() so the pool refills.
        """
        from app.services.container_pool import pool_registry

        pool = pool_registry.get_pool(lang_config.image)
        if pool is None:
            return None  # No pool for this image

        container = pool.acquire()
        if container is None:
            logger.info(f"[{exec_id}] Warm pool empty for {lang_config.image}, falling back")
            return None  # Pool exhausted — caller uses on-demand path

        logger.info(f"[{exec_id}] Using warm container {container.id[:8]}")

        try:
            # ---- Upload source file + stdin into container ---------------
            stdin_content = stdin_str if stdin_str.endswith("\n") else stdin_str + "\n"
            docker_service.put_files_to_container(
                container,
                files={
                    lang_config.source_file: request.code,
                    ".stdin_input": stdin_content,
                },
            )

            # ---- Compile step (Java, C++) --------------------------------
            if lang_config.compile:
                compile_timeout = settings.MAX_COMPILATION_TIME_SEC
                compile_timed_out, compile_exit, compile_stdout, compile_stderr, _ = (
                    docker_service.exec_in_warm_container(
                        container=container,
                        command=lang_config.compile,
                        timeout_sec=compile_timeout,
                        max_output_bytes=settings.MAX_STDOUT_SIZE_BYTES,
                    )
                )

                if compile_timed_out:
                    logger.info(f"[{exec_id}] Compilation timed out (warm)")
                    return ExecutionResponse(
                        success=False,
                        language=request.language,
                        stdout=compile_stdout,
                        stderr=f"Compilation timed out after {compile_timeout} seconds.",
                        exit_code=-1,
                        execution_time_ms=compile_timeout * 1000,
                        status=ExecutionStatus.COMPILATION_ERROR,
                        execution_id=exec_id,
                    )

                if compile_exit != 0:
                    logger.info(f"[{exec_id}] Compilation failed (warm), exit={compile_exit}")
                    return ExecutionResponse(
                        success=False,
                        language=request.language,
                        stdout=compile_stdout,
                        stderr=compile_stderr,
                        exit_code=compile_exit,
                        execution_time_ms=0,
                        status=ExecutionStatus.COMPILATION_ERROR,
                        execution_id=exec_id,
                    )

            # ---- Run step -----------------------------------------------
            # Always redirect stdin from .stdin_input (written above).
            run_cmd_str = " ".join(lang_config.run)
            run_command = ["sh", "-c", f"{run_cmd_str} < .stdin_input"]

            run_timeout = settings.MAX_EXECUTION_TIME_SEC
            timed_out, exit_code, stdout_str, stderr_str, duration_ms = (
                docker_service.exec_in_warm_container(
                    container=container,
                    command=run_command,
                    timeout_sec=run_timeout,
                    max_output_bytes=settings.MAX_STDOUT_SIZE_BYTES,
                )
            )

            if timed_out:
                logger.info(f"[{exec_id}] Execution timed out after {run_timeout}s (warm)")
                return ExecutionResponse(
                    success=False,
                    language=request.language,
                    stdout=stdout_str,
                    stderr="Execution timed out.",
                    exit_code=-1,
                    execution_time_ms=run_timeout * 1000,
                    status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
                    execution_id=exec_id,
                )

            if exit_code != 0:
                logger.info(f"[{exec_id}] Process exited non-zero ({exit_code}) (warm)")
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
                    execution_id=exec_id,
                )

            logger.info(f"[{exec_id}] Execution completed in {duration_ms}ms (warm)")
            return ExecutionResponse(
                success=True,
                language=request.language,
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=0,
                execution_time_ms=duration_ms,
                status=ExecutionStatus.COMPLETED,
                execution_id=exec_id,
            )

        except Exception as e:
            logger.error(
                f"[{exec_id}] Warm container execution failed: {e}",
                exc_info=True,
            )
            return None  # Fall back to on-demand

        finally:
            # Always recycle — even on error or timeout
            pool.release_and_replace(container)


execution_service = ExecutionService()
