# Local Testing Guide for MSQuant (macOS Development)

Since MSQuant is a Linux-only project (requires vLLM which doesn't support macOS), you'll need to use Docker to run quality checks locally before pushing.

## Prerequisites

- Docker installed on your Mac
- Working directory: `msquant/`

## Running Checks Locally

### Linting with Ruff

```bash
docker run --rm -v "$(pwd)":/app -w /app python:3.10-slim bash -c "pip install -q ruff && ruff check src"
```

Auto-fix:
```bash
docker run --rm -v "$(pwd)":/app -w /app python:3.10-slim bash -c "pip install -q ruff && ruff check --fix src"
```

### Type Checking with Pyright

Type checking requires the full dependency environment, so use the Pixi container with x86_64 platform:

```bash
docker run --rm --platform linux/amd64 -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi run typecheck
```

Note: This requires `pixi.lock` to exist (generated via `pixi install`). The `--platform linux/amd64` flag is required on Apple Silicon Macs since pixi.toml specifies `linux-64` only.

### Running Tests

```bash
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi run test
```

### Building Docker Image

```bash
cd docker
docker compose build
```

## Generating/Updating pixi.lock

If you modify `pixi.toml` dependencies, regenerate the lock file:

```bash
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi install
```

Then commit the updated `pixi.lock`.

## CI Workflow Simulation

To simulate what GitHub Actions will do:

```bash
# 1. Lint
docker run --rm -v "$(pwd)":/app -w /app python:3.10-slim bash -c "pip install -q ruff && ruff check src"

# 2. Type check  
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi run typecheck

# 3. Test
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi run test

# 4. Build
docker build -f docker/Dockerfile.gpu -t msquant:test .
```

## Common Issues

### "pixi.lock not found"
- Run `pixi install` via Docker to generate the lock file
- Commit `pixi.lock` to the repository

### "Platform not supported"
- pixi.toml specifies `platforms = ["linux-64"]` only
- All checks must run via Docker on Mac

### "libatomic.so.1 not found" when running pyright
- Use the `ghcr.io/prefix-dev/pixi:latest` container, not `python:3.10-slim`
- Pixi container has all necessary dependencies

## Quick Reference

```bash
# One-liner to run all checks
docker run --rm -v "$(pwd)":/app -w /app python:3.10-slim bash -c "pip install -q ruff && ruff check src" && \
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi run typecheck && \
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/prefix-dev/pixi:latest pixi run test && \
echo "All checks passed!"
