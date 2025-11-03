MSQuant Rebuild Guide: Python Version, Project Structure, Local Dev with Pixi, and CI/CD

1) Verified Python version to use

Conclusion: Use Python 3.10.x.

Evidence:
- Legacy Dockerfile base image: nvcr.io/nvidia/pytorch:24.06-py3
- NVIDIA release notes for 24.06: PyTorch is installed in /usr/local/lib/python3.10, i.e., container ships with Python 3.10
- Dependencies in legacy stack (transformers>=4.52.0, vllm>=0.11.0, llmcompressor, gradio>=4) all support Python 3.10; vLLM and Transformers also support 3.11/3.12, but Python 3.10 ensures maximum compatibility with the chosen NVIDIA container and CUDA/cuDNN stacks
Reference: https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-24-06.html

2) Proposed repository layout tailored to NiceGUI + Highcharts

Replace Gradio UI with NiceGUI while reusing the quantization engine and GPU monitor. Suggested structure:

msquant/
  README.md
  pixi.toml
  pixi.lock
  .pre-commit-config.yaml                  (optional but recommended)
  .github/
    workflows/
      ci.yml                               (PR build/test)
      docker-publish.yml                   (build+push on merge to main)
  docker/
    Dockerfile.gpu                         (NVIDIA runtime; prod image)
    docker-compose.yml                     (local compose with GPU)
  src/
    msquant/
      __init__.py
      app/                                 (NiceGUI application)
        __init__.py
        main.py                            (entrypoint, ui.run)
        pages/
          __init__.py
          home.py
          configure.py                     (quantization form)
          monitor.py                       (GPU monitor + logs)
          results.py
        components/
          __init__.py
          controls.py                      (reusable form widgets)
          dialogs.py
          layout.py                        (header/nav/footer)
        charts/
          __init__.py
          highcharts.py                    (helpers for nicegui-highcharts)
      core/
        __init__.py
        quantizer/
          __init__.py
          config.py                        (QuantizationConfig)
          engine.py                        (AWQQuantizer, NVFP4Quantizer, quantize)
        monitoring/
          __init__.py
          gpu_monitor.py                   (ported from legacy/gpu_monitor.py)
      services/
        __init__.py
        jobs.py                            (background task orchestration)
        storage.py                         (paths, HF caches, outputs)
      utils/
        __init__.py
        logging.py                         (stream callbacks, log formatting)

Notes:
- src/msquant/core/quantizer/* is a direct lift-and-organize from legacy/quantizer.py with minimal changes (split types/config/engine). Keep function signatures and behavior identical so quantization semantics remain stable.
- src/msquant/core/monitoring/gpu_monitor.py is lifted from legacy/gpu_monitor.py unchanged.
- src/msquant/app/pages/* implement NiceGUI pages: configure (form with validation), monitor (Highcharts charts for GPU), results (output directories), home (navigation).
- src/msquant/app/charts/highcharts.py holds helpers to build and update Highcharts options for NiceGUI.

3) Local developer setup with Pixi

We will use Pixi for local development environments and tasks. Python version is pinned to 3.10.*. We will use conda-forge for system-level dependencies and pypi-dependencies for packages not on conda-forge.

Example pixi.toml (place at repository root):

[project]
name = "msquant"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64"]

[tasks]
# Run the NiceGUI app (dev)
dev = { cmd = "python -m msquant.app.main", depends-on = ["install-plugins"] }
# Type checking
typecheck = "pyright src"
# Lint
lint = "ruff check src"
# Format
fmt = "ruff format src"
# Unit tests placeholder (pytest or hatch)
test = "pytest -q"
# Install optional NiceGUI plugin dynamically (Highcharts)
install-plugins = "python -c \"import importlib; import sys; sys.exit(0) if importlib.util.find_spec('nicegui_highcharts') else 1\"" 

[dependencies]
python = "3.10.*"
pip = "*"
# CLI/dev tools pinned for reproducibility
ruff = ">=0.6.9,<1.0"
pyright = ">=1.1.380,<2.0"
pytest = ">=8.1,<9.0"

[pypi-dependencies]
# UI
nicegui = ">=2.0.0"
nicegui-highcharts = ">=0.2.0"
# Quantization / ML stack used by the engine
vllm = ">=0.11.0"
llmcompressor = "*"
transformers = ">=4.52.0"
datasets = "*"
accelerate = "*"
safetensors = "*"
huggingface_hub = "*"
hf_transfer = "*"
tqdm = "*"
pandas = ">=2.2.0"
# Optional dev extras
types-tqdm = "*"

[feature.cuda]
# Placeholder; CUDA-enabled dev should rely on NVIDIA container. For CPU dev, keep default.
# If you must develop against local GPU with conda-forge CUDA packages, define an optional feature.

[environments]
# default environment
default = { solve-group = "default" }

Usage:

- Install Pixi: see https://pixi.sh/latest/installation/
- Create and activate env per task (Pixi runs in ephemeral shells):
  - pixi run dev                # run NiceGUI app locally
  - pixi run lint               # lint
  - pixi run fmt                # format
  - pixi run typecheck          # type-check
  - pixi run test               # run tests (if/when added)

Local execution notes:
- CPU-only local runs are sufficient for UI work (no quantization). Quantization requires NVIDIA GPU; use Docker compose below.
- If you need to exercise quantizer code paths without GPU, guard calls in services/jobs.py or use dry-run toggles.

4) NiceGUI application plan

- Pages
  - / (home): quick intro + navigation
  - /configure: form for quantization parameters (mirror legacy Gradio fields), submits to background job
  - /monitor: GPU metrics (reusing GPUMonitor), job logs (stream from job service), real-time charts via nicegui-highcharts
  - /results: list directories under /workspace/out (in container) or ./out locally; allow copy/download

- Components
  - panels for configuration, status, and control buttons
  - dialogs for confirmation/cancellation

- Background jobs
  - services/jobs.py: run quantize(config, log_callback=...) in a background thread; provide thread-safe queue for logs; expose job status
  - Use NiceGUI’s ui.timer to poll job status/log tail every N seconds; update components

- Highcharts
  - Use nicegui-highcharts (ui.highchart(options)) for:
    - GPU utilization (%)
    - Memory (%)
    - Temperature (°C)
    - Power (W)
  - Update series data via chart.options mutation + chart.update() in the timer callback

- Port mapping and defaults
  - NiceGUI defaults to port 8080; choose 8080 for new app (was 7860 for Gradio). Adjust docker-compose and docs accordingly.

5) Containerization (GPU runtime)

Dockerfile.gpu (place under docker/):

ARG BASE_IMAGE=nvcr.io/nvidia/pytorch:24.06-py3
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/workspace/hf \
    HF_DATASETS_CACHE=/workspace/hf/datasets \
    HF_HUB_ENABLE_HF_TRANSFER=1 \
    PYTHONUNBUFFERED=1

# System packages (if needed, keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python deps
RUN pip install --upgrade pip && \
    pip install \
      "nicegui>=2.0.0" \
      "nicegui-highcharts>=0.2.0" \
      "vllm>=0.11.0" \
      "llmcompressor" \
      "transformers>=4.52.0" \
      "datasets" "accelerate" "safetensors" \
      "huggingface_hub" "hf_transfer" "tqdm" \
      "pandas"

WORKDIR /workspace

# Copy source
# Assuming our code is in ./src/msquant. Adjust if different.
COPY src /workspace/src
ENV PYTHONPATH=/workspace/src

# Expose NiceGUI port
EXPOSE 8080

# Entrypoint
CMD ["python", "-m", "msquant.app.main"]

docker/docker-compose.yml:

services:
  msquant:
    build:
      context: ..
      dockerfile: docker/Dockerfile.gpu
    image: ghcr.io/OWNER/msquant:dev   # replace OWNER with your GitHub org/user
    container_name: msquant
    ports:
      - "8080:8080"
    environment:
      PYTORCH_CUDA_ALLOC_CONF: "expandable_segments:True,max_split_size_mb:64"
      HF_HOME: /workspace/hf
      HF_DATASETS_CACHE: /workspace/hf/datasets
      HF_HUB_ENABLE_HF_TRANSFER: "1"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ["0","2"]     # adjust for your host
              capabilities: ["gpu"]
    volumes:
      - ../hf:/workspace/hf
      - ../out:/workspace/out
    runtime: nvidia
    # Or for compose v2+. Alternatively set: --gpus '"device=0,2"' via deploy section on Swarm.

Local run:
- From docker/ directory: docker compose up --build
- Browse http://localhost:8080

6) CI/CD with GitHub Actions

We will use:
- prefix-dev/setup-pixi for CI environment (lint/typecheck/tests/build)
- docker/build-push-action for image build/publish
- ghcr.io (GitHub Container Registry) as default registry; tokens come from GITHUB_TOKEN

A) CI for PRs (build/test only; no push)

.github/workflows/ci.yml:

name: CI (PR)
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: ["**"]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Pixi
        uses: prefix-dev/setup-pixi@v0
        with:
          pixi-version: "latest"  # Consider pinning to a specific release
          cache: true

      - name: Lint
        run: pixi run lint

      - name: Typecheck
        run: pixi run typecheck

      - name: Unit tests
        run: pixi run test

      - name: Build container (no push)
        uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/Dockerfile.gpu
          push: false
          load: true
          tags: msquant:pr-${{ github.sha }}

Notes:
- If your repo is private or you need extra auth for dependencies, add steps accordingly.
- If you prefer to run commands within the Pixi env without prefixing each step, you can set shell: pixi run bash -e {0} (custom shell wrapper). Reference: https://pixi.sh/latest/integration/ci/github_actions/ and https://github.com/prefix-dev/setup-pixi

B) Build and push on PR merge (push to main)

.github/workflows/docker-publish.yml:

name: Docker Publish
on:
  push:
    branches:
      - main
    # optional: tag releases as well
    # tags:
    #   - "v*.*.*"

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write   # required for GHCR
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/msquant
          tags: |
            type=raw,value=latest
            type=sha,prefix=sha-,format=short

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/Dockerfile.gpu
          push: true
          platforms: linux/amd64
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

Notes:
- The push event on main occurs when a PR is merged, satisfying “build and push on PR merge.”
- Images published: ghcr.io/OWNER/msquant:latest and ghcr.io/OWNER/msquant:sha-<short>.
- To enable multi-arch, add linux/arm64 if your base supports it (NVIDIA CUDA containers typically do not; keep linux/amd64).

C) (Optional) Automatic lockfile updates (Pixi)
Reference: https://pixi.sh/latest/integration/ci/updates_github_actions/
You can configure a scheduled workflow using pavelzw/pixi-diff-to-markdown to periodically refresh pixi.lock and open PRs.

7) Migration mapping: Gradio to NiceGUI

Legacy features to port:
- Quantization form, validation, job start/stop → NiceGUI form components (ui.input, ui.select, ui.checkbox, ui.radio, ui.button). Backed by services/jobs.py which calls core.quantizer.quantize in a background thread.
- Streaming logs → keep the QuantizationLogger callback buffering in memory; poll with ui.timer and update a ui.markdown or a NiceGUI text area.
- GPU monitor → reuse GPUMonitor; present four Highcharts line charts. Populate series from monitor.get_history(k) in a ui.timer callback. Add GPU selector and metrics summary.
- Output dirs listing → scan /workspace/out (container) or ./out (local) and present with ui.table; provide download/serve static if desired.

8) Operational conventions and environment

- Model caches and outputs
  - Honor HF_HOME=/workspace/hf and HF_DATASETS_CACHE=/workspace/hf/datasets (same as legacy).
  - Outputs under /workspace/out (mounted to ./out by Compose).

- Ports
  - Container exposes 8080; map host 8080:8080.

- Security and GPU constraints
  - This app is intended for inside-trusted networks or behind auth. If external, enforce auth (FastAPI mount or proxy-layer).
  - Compose example pins GPUs ["0","2"] as in legacy; adjust for your host.

9) Implementation checklist

- Port quantizer.py into src/msquant/core/quantizer/{config.py,engine.py} without altering behavior.
- Port gpu_monitor.py to src/msquant/core/monitoring/gpu_monitor.py unchanged.
- Implement NiceGUI pages and link nav; wire background jobs and timers.
- Verify that vLLM, llmcompressor, transformers interplay remains unchanged in quantizer engine.
- Validate Docker build and run with sample quantization on a CUDA host.
- Land CI workflows; confirm PR build/test and main push publish images to GHCR.

10) References

- Setup Pixi (GitHub Action):
  - GitHub: https://github.com/prefix-dev/setup-pixi
  - Docs: https://pixi.sh/latest/integration/ci/github_actions/
  - Marketplace: https://github.com/marketplace/actions/setup-pixi

- Pixi Project:
  - GitHub: https://github.com/prefix-dev/pixi
  - Docs: https://pixi.sh/latest/

- NVIDIA PyTorch 24.06 (Python 3.10 path evidence):
  - https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-24-06.html

Appendix: Developer quickstart

- Local (UI only): 
  - pixi run dev
  - Visit http://localhost:8080
- GPU compose (end-to-end):
  - cd docker && docker compose up --build
  - Visit http://localhost:8080
- CI (PR):
  - On PR open/synchronize, Action runs lint/typecheck/tests and builds the container
- Publish:
  - On merge to main, Docker image builds and pushes to ghcr.io/OWNER/msquant with latest and sha- tags

This guide contains precise versions, structure, and CI/CD definitions so an engineering agent can implement without guessing.