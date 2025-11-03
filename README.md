# MSQuant

Model Quantization Tool with NiceGUI interface for AWQ and NVFP4 quantization methods.

## Features

- **Quantization Methods**
  - AWQ (Activation-aware Weight Quantization): 4-bit integer quantization
  - NVFP4 (NVIDIA FP4): 4-bit floating-point quantization

- **Web Interface**
  - Real-time GPU monitoring with visual charts (Highcharts)
  - Streaming logs during quantization
  - Robust job cancellation (terminates subprocess and all children)
  - Easy configuration forms
  - Output model management

- **Infrastructure**
  - Docker support with NVIDIA GPU runtime
  - CI/CD with GitHub Actions
  - Local development with Pixi

## Requirements

- Python 3.10+
- NVIDIA GPU with CUDA support (for quantization)
- Docker with NVIDIA runtime (for containerized deployment)

## Quick Start

### Local Development (CPU only, UI testing)

```bash
# Install Pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Run the application
pixi run dev
```

Visit http://localhost:8080

### Docker Deployment (with GPU)

```bash
cd docker
docker compose up --build
```

Visit http://localhost:8080

### Configuration

Environment variables:
- `HF_HOME`: HuggingFace cache directory (default: `/workspace/hf`)
- `HF_DATASETS_CACHE`: Datasets cache directory (default: `/workspace/hf/datasets`)
- `OUT_DIR`: Output directory for quantized models (default: `/workspace/out`)
- `PORT`: Application port (default: `8080`)

## Project Structure

```
msquant/
├── src/
│   └── msquant/
│       ├── app/                # NiceGUI application
│       │   ├── main.py        # Application entry point
│       │   ├── pages/         # UI pages
│       │   └── components/    # Reusable UI components
│       ├── core/              # Core functionality
│       │   ├── quantizer/     # Quantization engine
│       │   └── monitoring/    # GPU monitoring
│       └── services/          # Background services
├── docker/                    # Docker configuration
│   ├── Dockerfile.gpu
│   └── docker-compose.yml
├── .github/
│   └── workflows/             # CI/CD workflows
├── pixi.toml                  # Pixi configuration
└── README.md
```

## Development

### Available Commands

```bash
# Run development server
pixi run dev

# Lint code
pixi run lint

# Format code
pixi run fmt

# Type checking
pixi run typecheck

# Run tests
pixi run test
```

### Adding Dependencies

Edit `pixi.toml`:
- Add to `[dependencies]` for conda packages
- Add to `[pypi-dependencies]` for PyPI packages

Then run:
```bash
pixi install
```

## Usage

### 1. Configure Quantization

Navigate to the **Configure** page and set:
- Model ID (e.g., `meta-llama/Llama-3.1-8B`)
- Quantization method (AWQ or NVFP4)
- Calibration dataset settings
- Method-specific parameters

**Note:** Output format is determined by the quantization backend. The saved checkpoint format follows the backend's default conventions.

### 2. Monitor Progress

The **Monitor** page shows:
- Job status and logs with streaming updates
- Real-time GPU metrics with visual charts (utilization, memory, temperature, power)
- GPU selector for multi-GPU systems
- Cancel button to terminate running jobs

### 3. Access Results

The **Results** page lists:
- Quantized model outputs
- Cache information
- Model sizes and paths

## CI/CD

### Pull Requests

On PR open/update:
- Linting and type checking
- Unit tests
- Docker build (no push)

### Main Branch

On merge to main:
- Docker image build and push to GHCR
- Tagged with `latest` and `sha-<commit>`

## Docker Images

Images are published to GitHub Container Registry:

```bash
# Pull latest
docker pull ghcr.io/OWNER/msquant:latest

# Pull specific commit
docker pull ghcr.io/OWNER/msquant:sha-abc1234
```

Replace `OWNER` with your GitHub username/organization.

## License

[Add your license here]

## Credits

Built with:
- [NiceGUI](https://nicegui.io/) - Web interface
- [llmcompressor](https://github.com/vllm-project/llm-compressor) - Quantization engine
- [vLLM](https://github.com/vllm-project/vllm) - LLM inference
- [Pixi](https://pixi.sh/) - Package management
