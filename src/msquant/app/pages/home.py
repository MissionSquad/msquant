"""Home page for MSQuant application."""
from nicegui import ui


def create_home_page():
    """Create the home page."""
    with ui.column().classes('w-full items-center justify-center gap-8 p-8'):
        ui.label('MSQuant').classes('text-6xl font-bold')
        ui.label('Model Quantization Tool').classes('text-2xl text-gray-600')
        
        with ui.card().classes('w-full max-w-4xl'):
            ui.label('Welcome to MSQuant').classes('text-2xl font-bold mb-4')
            ui.markdown('''
MSQuant provides a simple interface for quantizing large language models using:

- **AWQ (Activation-aware Weight Quantization)**: 4-bit integer quantization with high accuracy
- **NVFP4 (NVIDIA FP4)**: 4-bit floating-point quantization for NVIDIA GPUs

### Features

- Real-time GPU monitoring with visual charts
- Support for multiple quantization methods
- Streaming logs during quantization
- Output model management

### Quick Start

1. **Configure** - Set up your quantization parameters
2. **Monitor** - Watch GPU metrics and job progress  
3. **Results** - Access your quantized models

Navigate using the menu above to get started.
            ''')
        
        with ui.row().classes('gap-4 mt-4'):
            ui.button('Configure Quantization', on_click=lambda: ui.navigate.to('/configure')).props('size=lg color=primary')
            ui.button('Monitor Jobs', on_click=lambda: ui.navigate.to('/monitor')).props('size=lg')
            ui.button('View Results', on_click=lambda: ui.navigate.to('/results')).props('size=lg')
