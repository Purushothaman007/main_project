import os
import time
import socket
import requests
import docker
from docker.errors import DockerException, ImageNotFound, APIError
from typing import Dict, List, Tuple, Optional
from app.core.config import settings
from app.core.logging_config import logger

class DockerService:
    def __init__(self):
        self._client = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    def is_reachable(self) -> bool:
        """Check if Docker daemon is responsive."""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Docker ping failed: {e}")
            return False

    def check_images_exist(self, image_names: List[str]) -> Dict[str, bool]:
        """Check availability of required Docker images."""
        result = {}
        for img in image_names:
            try:
                self.client.images.get(img)
                result[img] = True
            except ImageNotFound:
                result[img] = False
            except Exception as e:
                logger.error(f"Error checking image {img}: {e}")
                result[img] = False
        return result

    def execute_in_container(
        self,
        image: str,
        command: List[str],
        workspace_dir: str,
        stdin: str = "",
        timeout_sec: int = 20,
        max_output_bytes: int = 1 * 1024 * 1024
    ) -> Tuple[bool, int, str, str, int, bool]:

        container = None
        start_time = time.perf_counter()

        timed_out = False
        output_exceeded = False
        exit_code = -1

        stdout_str = ""
        stderr_str = ""

        try:
            mounts = {
                workspace_dir: {
                    "bind": "/app",
                    "mode": "rw"
                }
            }

            exec_cmd = command
            if stdin:
                stdin_file_path = os.path.join(workspace_dir, ".stdin_input")
                with open(stdin_file_path, "w", encoding="utf-8") as f:
                    f.write(stdin)
                    if not stdin.endswith("\n"):
                        f.write("\n")
                exec_cmd = ["sh", "-c", f"{' '.join(command)} < .stdin_input"]

            t_create_start = time.perf_counter()
            container = self.client.containers.create(
                image=image,
                command=exec_cmd,
                volumes=mounts,
                working_dir="/app",
                network_disabled=True,
                mem_limit=settings.MEMORY_LIMIT,
                memswap_limit=settings.MEMORY_LIMIT,
                nano_cpus=int(settings.CPU_LIMIT * 1e9),
                pids_limit=settings.MAX_PIDS,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                user="1000:1000",
                stdin_open=False,
                tty=False,
                detach=True
            )
            t_create_ms = int((time.perf_counter() - t_create_start) * 1000)

            t_start_start = time.perf_counter()
            container.start()
            t_start_ms = int((time.perf_counter() - t_start_start) * 1000)

            # Wait for container to finish
            t_wait_start = time.perf_counter()
            try:
                result = container.wait(timeout=timeout_sec)
                exit_code = result.get("StatusCode", -1)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, socket.timeout, TimeoutError, Exception) as te:
                if "timeout" in str(te).lower() or "timed out" in str(te).lower() or isinstance(te, (socket.timeout, TimeoutError)):
                    timed_out = True
                    logger.warning(f"Container execution exceeded {timeout_sec} seconds")
                    try:
                        container.kill()
                    except Exception:
                        pass
                    try:
                        container.wait(timeout=2)
                    except Exception:
                        pass
                else:
                    try:
                        container.reload()
                        if container.status == "running":
                            timed_out = True
                            try:
                                container.kill()
                            except Exception:
                                pass
                            try:
                                container.wait(timeout=2)
                            except Exception:
                                pass
                    except Exception:
                        pass
            t_wait_ms = int((time.perf_counter() - t_wait_start) * 1000)

            end_time = time.perf_counter()
            duration_ms = int(
                (end_time - start_time) * 1000
            )

            # Get stdout
            t_stdout_start = time.perf_counter()
            try:
                stdout_bytes = container.logs(
                    stdout=True,
                    stderr=False
                )
            except Exception:
                stdout_bytes = b""
            t_stdout_ms = int((time.perf_counter() - t_stdout_start) * 1000)

            # Get stderr
            t_stderr_start = time.perf_counter()
            try:
                stderr_bytes = container.logs(
                    stdout=False,
                    stderr=True
                )
            except Exception:
                stderr_bytes = b""
            t_stderr_ms = int((time.perf_counter() - t_stderr_start) * 1000)

            # Enforce output limit
            if len(stdout_bytes) > max_output_bytes:
                output_exceeded = True
                stdout_bytes = stdout_bytes[:max_output_bytes]

            if len(stderr_bytes) > max_output_bytes:
                output_exceeded = True
                stderr_bytes = stderr_bytes[:max_output_bytes]

            stdout_str = stdout_bytes.decode(
                "utf-8",
                errors="replace"
            )

            stderr_str = stderr_bytes.decode(
                "utf-8",
                errors="replace"
            )

            logger.info(
                f"[STAGE TIMING] Command: {' '.join(command)} | "
                f"Create: {t_create_ms}ms | Start+Stdin: {t_start_ms}ms | "
                f"Wait: {t_wait_ms}ms | StdoutLogs: {t_stdout_ms}ms | "
                f"StderrLogs: {t_stderr_ms}ms | TotalStage: {duration_ms}ms"
            )

            return (
                timed_out,
                exit_code,
                stdout_str,
                stderr_str,
                duration_ms,
                output_exceeded
            )

        except Exception as e:

            logger.error(
                f"Docker execution error: {e}",
                exc_info=True
            )

            raise

        finally:

            # ALWAYS remove the container
            if container:
                t_remove_start = time.perf_counter()
                try:
                    container.remove(force=True)
                    t_remove_ms = int((time.perf_counter() - t_remove_start) * 1000)
                    logger.info(
                        f"[STAGE TIMING] Container {container.id[:8]} removed in {t_remove_ms}ms"
                    )

                except Exception as e:

                    logger.warning(
                        f"Failed to remove container "
                        f"{container.id[:8]}: {e}"
                    )
docker_service = DockerService()
