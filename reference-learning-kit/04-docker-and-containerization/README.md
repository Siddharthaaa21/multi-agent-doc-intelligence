# 🐳 Module 04: Docker, Multi-Stage Builds & Container Orchestration

## 1. Why ML Engineers Need Production Docker Practices
In ML notebooks, environments are often configured ad-hoc (`pip install` without pinned versions, global CUDA drivers). In production SDE-1 systems:
- Environments must be **hermetic, reproducible, and immutable**.
- Containers must be **minimal in size** (fast deployment in CI/CD and Kubernetes).
- Containers must run as **non-root users** to meet enterprise security audits.

---

## 2. Core Concepts

### A. Docker Layer Caching (The Invalidation Rule)
Docker builds images layer by layer. If a line in a Dockerfile changes, **all subsequent layers are invalidated and must be rebuilt**.

```dockerfile
# ❌ BAD: Any 1-character code edit invalidates cache and triggers full pip install!
COPY . .
RUN pip install -r backend/requirements.txt

# ✅ GOOD: Dependencies are cached independently of code edits
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
```

---

### B. Multi-Stage Builds
Why multi-stage?
- **Stage 1 (Builder)**: Installs heavy compilers (`gcc`, `g++`, `python3-dev`) and builds wheels.
- **Stage 2 (Runtime)**: Copies only the pre-compiled Python packages into a clean, minimal `python:3.11-slim` base image without build tools.
- **Result**: Reduces final image size from ~1.4GB to <200MB, improves startup latency, and closes CVE security vulnerabilities.

---

### C. Docker Compose Service Discovery
In `docker-compose.yml`, services communicate using their **service name as the DNS hostname**:
- From the backend container, PostgreSQL is reachable at `host: postgres`, port `5432`.
- No hardcoded IP addresses (`localhost` inside a container refers to that container itself, not your host machine!).

---

## 3. Included Artifacts in this Module

1. [`Dockerfile.example`](./Dockerfile.example): Production multi-stage Python backend image with non-root security.
2. [`docker-compose.example.yml`](./docker-compose.example.yml): Full multi-service architecture with FastAPI, PostgreSQL, Healthchecks, and persistent volume storage.
