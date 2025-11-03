"""Monitor page for tracking job progress and GPU metrics."""
from nicegui import ui

from msquant.services import JobService
from msquant.core.monitoring import GPUMonitor
from msquant.app.charts.highcharts import build_line_chart, convert_history_to_chart_data


def create_monitor_page(job_service: JobService, gpu_monitor: GPUMonitor):
    """Create the monitor page with real-time charts."""
    
    # State for selected GPU
    selected_gpu_index = {"value": 0}
    available_gpus = {"list": []}
    
    with ui.column().classes('w-full p-8 gap-4'):
        ui.label('Job Monitor').classes('text-4xl font-bold')
        
        # Job status card
        with ui.card().classes('w-full'):
            ui.label('Job Status').classes('text-2xl font-bold mb-4')
            status_label = ui.label('Status: IDLE')
            
            # Log viewer
            ui.label('Job Logs').classes('text-xl font-bold mt-4 mb-2')
            log_output = ui.textarea().classes('w-full font-mono').props('readonly rows=15')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Refresh Status', on_click=lambda: update_status())
                cancel_btn = ui.button('Cancel Job', on_click=lambda: cancel_job()).props('color=negative')
        
        # GPU metrics card
        with ui.card().classes('w-full'):
            ui.label('GPU Metrics').classes('text-2xl font-bold mb-4')
            
            # GPU selector
            with ui.row().classes('gap-4 items-center mb-4'):
                ui.label('Select GPU:')
                gpu_select = ui.select(
                    options=[],
                    value=0,
                    on_change=lambda e: on_gpu_select(e.value)
                ).classes('w-48')
            
            # Text summary
            gpu_summary = ui.markdown('').classes('mb-4')
            
            # GPU Charts
            ui.label('Real-time Metrics').classes('text-xl font-bold mb-2')
            
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Utilization chart
                util_chart = ui.highchart(
                    build_line_chart("GPU Utilization", "Utilization", "%", y_max=100)
                ).classes('w-full')

                # Memory chart
                mem_chart = ui.highchart(
                    build_line_chart("GPU Memory", "Memory", "%", y_max=100)
                ).classes('w-full')

                # Temperature chart
                temp_chart = ui.highchart(
                    build_line_chart("GPU Temperature", "Temperature", "°C")
                ).classes('w-full')

                # Power chart
                power_chart = ui.highchart(
                    build_line_chart("GPU Power", "Power", "W")
                ).classes('w-full')
            
            charts = {
                'utilization': util_chart,
                'memory': mem_chart,
                'temperature': temp_chart,
                'power': power_chart
            }
        
        def update_status():
            """Update job status and logs."""
            status = job_service.get_status()
            status_label.text = f'Status: {status.value.upper()}'
            
            # Enable/disable cancel button based on status
            cancel_btn.props(f'disable={status.value != "running"}')
            
            # Get logs
            logs = job_service.get_logs(last_n=100)
            log_output.value = '\n'.join(logs) if logs else 'No logs yet...'
            
            # Show result or error
            if status.value == 'completed':
                result = job_service.get_result()
                if result:
                    ui.notify(f'Job completed! Output: {result}', type='positive')
            elif status.value == 'failed':
                error = job_service.get_error()
                if error:
                    ui.notify(f'Job failed: {error}', type='negative')
            elif status.value == 'cancelled':
                ui.notify('Job was cancelled', type='warning')
        
        def cancel_job():
            """Cancel the current job."""
            job_service.cancel_job()
            ui.notify('Job cancellation requested', type='warning')
            update_status()
        
        def update_gpu_metrics():
            """Update GPU metrics display and charts."""
            gpus = gpu_monitor.query_gpus()
            
            # Update available GPUs list
            if gpus:
                gpu_options = [
                    {"label": f"GPU {gpu.index}: {gpu.name}", "value": gpu.index}
                    for gpu in gpus
                ]
                
                if gpu_options != available_gpus["list"]:
                    available_gpus["list"] = gpu_options
                    gpu_select.options = gpu_options
                    if selected_gpu_index["value"] not in [g.index for g in gpus]:
                        selected_gpu_index["value"] = gpus[0].index
                        gpu_select.value = gpus[0].index
            
            # Update text summary
            summary = gpu_monitor.format_summary(gpus)
            gpu_summary.content = summary
            
            # Update charts if available
            if charts and gpus:
                current_gpu = selected_gpu_index["value"]
                history = gpu_monitor.get_history(current_gpu)
                
                if history:
                    timestamps = [gpu.timestamp for gpu in history]
                    
                    # Utilization
                    util_data = convert_history_to_chart_data(
                        timestamps,
                        [gpu.utilization for gpu in history]
                    )
                    charts['utilization'].options['series'][0]['data'] = util_data
                    charts['utilization'].update()
                    
                    # Memory
                    mem_data = convert_history_to_chart_data(
                        timestamps,
                        [gpu.memory_percent for gpu in history]
                    )
                    charts['memory'].options['series'][0]['data'] = mem_data
                    charts['memory'].update()
                    
                    # Temperature
                    temp_data = convert_history_to_chart_data(
                        timestamps,
                        [gpu.temperature for gpu in history]
                    )
                    charts['temperature'].options['series'][0]['data'] = temp_data
                    charts['temperature'].update()
                    
                    # Power
                    power_data = convert_history_to_chart_data(
                        timestamps,
                        [gpu.power_draw for gpu in history]
                    )
                    charts['power'].options['series'][0]['data'] = power_data
                    charts['power'].update()
        
        def on_gpu_select(value):
            """Handle GPU selection change."""
            selected_gpu_index["value"] = value
            update_gpu_metrics()
        
        # Auto-refresh timers
        ui.timer(2.0, lambda: update_status())
        ui.timer(1.0, lambda: update_gpu_metrics())
        
        # Initial update
        update_status()
        update_gpu_metrics()
