# Security Architecture & Arbitrary Code Execution Review

## Threat Model & Attack Vectors

In a browser-based programming laboratory, students are provided an interface to execute arbitrary code. The core threat model assumes that **every code submission is potentially malicious** and actively attempting to exploit the underlying infrastructure.

---

## Security Requirements Audit & Enforcement

### 1. Host Isolation & No Host Execution
* **Threat:** Malicious student code escaping to the host OS.
* **Mitigation:** Code execution is strictly contained within Docker Linux containers. Code files are written to transient temporary directories (`/tmp/code_exec_xxxx`) mounted into the container as `/app`. Code never executes directly on the host.

### 2. Network Isolation
* **Threat:** Exfiltration of internal credentials, port scanning of internal college subnet, or participation in botnets/DDoS.
* **Mitigation:** `network_disabled=True` is explicitly passed to container creation. Virtual network interfaces are disabled inside the container. Automated tests confirm socket creation and external HTTP connections fail.

### 3. Container Escapes & Privilege Escalation
* **Threat:** Kernel exploits, container escape via root privileges or Docker socket access.
* **Mitigation:**
  - `user="1000:1000"`: Containers run under an unprivileged `sandbox` user (UID 1000).
  - `cap_drop=["ALL"]`: Drops all Linux kernel capabilities (including `CAP_SYS_ADMIN`, `CAP_NET_RAW`, `CAP_SYS_PTRACE`).
  - `security_opt=["no-new-privileges:true"]`: Prevents binaries (like `setuid` / `setgid`) from gaining elevated permissions.
  - `--privileged`: Strict rule prohibiting `--privileged` flags.

### 4. Denial of Service & Resource Exhaustion Vectors

| Attack Vector | Security Limit | Enforcement Mechanism |
| :--- | :--- | :--- |
| **CPU Starvation / Infinite Loops** | 1 CPU Core / 5s Timeout | `nano_cpus=1000000000`, wall-clock timeout container termination |
| **Memory Exhaustion (OOM)** | 256 MB RAM | `mem_limit="256m"`, `memswap_limit="256m"` (disables swap spillover) |
| **Fork Bombs / Thread Flooding** | 64 PIDs | `pids_limit=64` restricts total process & thread spawn capacity |
| **Disk Exhaustion (Infinite Print)** | 1 MB Log Cap | Output streaming truncates stdout/stderr logs beyond 1MB |
| **Payload Flooding** | 100 KB Source / Stdin | Request payloads >100KB rejected before touching Docker daemon |

### 5. Information Leakage Prevention
* **Threat:** Exposing internal host directory structures, database URIs, environment variables, or Docker container IDs to end-users via error tracebacks.
* **Mitigation:** Unhandled backend exceptions are caught at the API boundary, logged internally with a unique `execution_id`, and returned to the client as a generic `SYSTEM_ERROR` message.

---

## Residual Risks & Recommendations for Module 2+

1. **Host Kernel Shared Vulnerabilities:**
   - *Risk:* Containers share the host Linux kernel (or WSL2 kernel). Zero-day Linux kernel privilege escalation exploits could theoretically affect the host.
   - *Mitigation for Future:* Integrate gVisor (`runsc`) or Kata Containers to provide hypervisor-level microVM isolation per execution.

2. **Docker Daemon Access:**
   - *Risk:* Access to the Docker socket `/var/run/docker.sock` grants root equivalence on the host.
   - *Mitigation:* Ensure the FastAPI backend runs under a dedicated, low-privilege user account and communicates with Docker daemon over secured local sockets only.
