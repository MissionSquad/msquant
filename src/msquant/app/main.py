"""
MSQuant NiceGUI Application Entry Point.
"""
import os
from nicegui import ui, app

from msquant.app.pages import home, configure, monitor, results
from msquant.app.components.layout import create_header
from msquant.services import JobService, StorageService
from msquant.core.monitoring import GPUMonitor


# Initialize services
job_service = JobService()
storage_service = StorageService(
    out_dir=os.environ.get("OUT_DIR", "/workspace/out"),
    hf_home=os.environ.get("HF_HOME", "/workspace/hf"),
    hf_datasets_cache=os.environ.get("HF_DATASETS_CACHE", "/workspace/hf/datasets"),
)
gpu_monitor = GPUMonitor(history_size=60)

# Store in app storage for access by pages
app.storage.general['job_service'] = job_service
app.storage.general['storage_service'] = storage_service
app.storage.general['gpu_monitor'] = gpu_monitor


def init_routes():
    """Initialize application routes."""
    
    @ui.page('/')
    def index_page():
        create_header()
        home.create_home_page()
    
    @ui.page('/configure')
    def configure_page():
        create_header()
        configure.create_configure_page(job_service, storage_service)
    
    @ui.page('/monitor')
    def monitor_page():
        create_header()
        monitor.create_monitor_page(job_service, gpu_monitor)
    
    @ui.page('/results')
    def results_page():
        create_header()
        results.create_results_page(storage_service)


def main():
    """Main application entry point."""
    # Initialize routes
    init_routes()
    
    # Configure app
    ui.run(
        title='MSQuant',
        port=int(os.environ.get("PORT", 8080)),
        host='0.0.0.0',
        reload=False,
        show=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
