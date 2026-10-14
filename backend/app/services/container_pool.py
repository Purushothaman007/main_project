import io
import tarfile
import threading
import queue
from typing import Optional, Dict

import docker
from docker.errors import DockerException, APIError

from app.core.config import settings
from app.core.logging_config import logger


class ContainerPool:
    """
    Maintains a queue of pre-warmed, already-started containers for one Docker image.

    Each container runs 'sleep infinity' and consumes minimal resources while idle.
    All security constraints (resource limits, network disabled, capability drops,
    non-root user) are applied at create time and remain in effect for exec calls.

    Lifecycle:
        initialize()              → fills queue with pool_size containers
        acquire()                 → pops one container (non-blocking, returns None if empty)
        release_and_replace(c)   → destroys c, spawns replacement in background daemon thread
        shutdown()                → drains and removes all idle containers
    """

    def __init__(self, image: str, pool_size: int, client: docker.DockerClient):
        self.image = image
        self.pool_size = pool_size
        self._client = client
        self._pool: queue.Queue = queue.Queue()
        self._shutdown = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Pre-warm pool_size containers. Called once at server startup."""
        logger.info(f"[Pool:{self.image}] Pre-warming {self.pool_size} containers...")
        for i in range(self.pool_size):
            try:
                c = self._spawn()
                self._pool.put(c)
                logger.info(
                    f"[Pool:{self.image}] Container {c.id[:8]} ready "
                    f"({i + 1}/{self.pool_size})"
                )
            except Exception as e:
                logger.error(
                    f"[Pool:{self.image}] Failed to pre-warm container "
                    f"{i + 1}/{self.pool_size}: {e}"
                )

    def acquire(self) -> Optional[docker.models.containers.Container]:
        """
        Pop a warm container from the queue (non-blocking).
        Returns None if the pool is currently empty — caller must fall back
        to on-demand container creation.
        """
        try:
            return self._pool.get_nowait()
        except queue.Empty:
            return None

    def release_and_replace(
        self, container: docker.models.containers.Container
    ) -> None:
        """
        Destroy the used container and spawn a replacement in a background
        daemon thread so the caller is never blocked.
        """
        def _work():
            # 1. Destroy the used container
            try:
                container.remove(force=True)
                logger.debug(
                    f"[Pool:{self.image}] Removed used container {container.id[:8]}"
                )
            except Exception as e:
                logger.warning(
                    f"[Pool:{self.image}] Could not remove container "
                    f"{container.id[:8]}: {e}"
                )

            # 2. Spawn a fresh replacement (unless we are shutting down)
            if not self._shutdown:
                try:
                    new = self._spawn()
                    self._pool.put(new)
                    logger.debug(
                        f"[Pool:{self.image}] Replacement container "
                        f"{new.id[:8]} ready"
                    )
                except Exception as e:
                    logger.error(
                        f"[Pool:{self.image}] Failed to spawn replacement: {e}"
                    )

        threading.Thread(target=_work, daemon=True).start()

    def shutdown(self) -> None:
        """Drain and forcefully remove all idle containers. Called at server shutdown."""
        self._shutdown = True
        logger.info(f"[Pool:{self.image}] Shutting down, draining idle containers...")
        removed = 0
        while not self._pool.empty():
            try:
                c = self._pool.get_nowait()
                c.remove(force=True)
                removed += 1
            except Exception:
                pass
        logger.info(f"[Pool:{self.image}] Removed {removed} idle container(s).")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _spawn(self) -> docker.models.containers.Container:
        """Create a new idle container and start it."""
        container = self._client.containers.create(
            image=self.image,
            command=["sleep", "infinity"],   # keeps container alive, zero CPU
            working_dir="/app",
            network_disabled=True,
            mem_limit=settings.MEMORY_LIMIT,
            nano_cpus=int(settings.CPU_LIMIT * 1e9),
            pids_limit=settings.MAX_PIDS,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],
            user="1000:1000",
            stdin_open=False,
            tty=False,
            detach=True,
        )
        container.start()
        return container


# ---------------------------------------------------------------------------
# Global registry — one ContainerPool per unique Docker image
# ---------------------------------------------------------------------------

class PoolRegistry:
    """
    Manages one ContainerPool per Docker image.
    Initialised once at application startup via initialize().
    """

    POOL_SIZE = 2  # warm containers per image

    def __init__(self):
        self._pools: Dict[str, ContainerPool] = {}

    def initialize(
        self,
        client: docker.DockerClient,
        language_configs: dict,
    ) -> None:
        """
        Build one pool per unique image referenced by language_configs.
        Safe to call even if Docker is temporarily unavailable — pools for
        unavailable images are simply skipped with a warning.
        """
        seen_images: set = set()
        for lang, config in language_configs.items():
            image = config.image
            if image in seen_images:
                continue
            seen_images.add(image)

            pool = ContainerPool(image=image, pool_size=self.POOL_SIZE, client=client)
            try:
                pool.initialize()
                self._pools[image] = pool
            except Exception as e:
                logger.error(
                    f"[PoolRegistry] Could not initialize pool for image "
                    f"'{image}': {e}"
                )

        logger.info(
            f"[PoolRegistry] Ready — pools active for "
            f"{len(self._pools)}/{len(seen_images)} image(s)."
        )

    def get_pool(self, image: str) -> Optional[ContainerPool]:
        return self._pools.get(image)

    def shutdown(self) -> None:
        for pool in self._pools.values():
            pool.shutdown()
        self._pools.clear()


# Singleton used across the application
pool_registry = PoolRegistry()
