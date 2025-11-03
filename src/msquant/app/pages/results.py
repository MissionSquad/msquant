"""Results page for viewing quantized model outputs."""
from nicegui import ui
from msquant.services import StorageService


def create_results_page(storage_service: StorageService):
    """Create the results page."""
    
    with ui.column().classes('w-full p-8 gap-4'):
        ui.label('Quantized Models').classes('text-4xl font-bold mb-4')
        
        # Cache info card
        with ui.card().classes('w-full'):
            ui.label('Cache Information').classes('text-2xl font-bold mb-4')
            cache_info_display = ui.markdown('')
            
            def update_cache_info():
                """Update cache information display."""
                cache_info = storage_service.get_cache_info()
                content = []
                for name, info in cache_info.items():
                    content.append(f"**{name}**")
                    content.append(f"- Path: `{info['path']}`")
                    content.append(f"- Exists: {info['exists']}")
                    content.append(f"- Size: {info['size']}")
                    content.append("")
                cache_info_display.content = '\n'.join(content)
            
            update_cache_info()
        
        # Output models card
        with ui.card().classes('w-full'):
            ui.label('Output Models').classes('text-2xl font-bold mb-4')
            
            outputs_container = ui.column().classes('w-full gap-2')
            
            def update_outputs():
                """Update list of output models."""
                outputs_container.clear()
                outputs = storage_service.list_outputs()
                
                if not outputs:
                    with outputs_container:
                        ui.label('No quantized models yet. Run a quantization job to create outputs.')
                else:
                    with outputs_container:
                        # Create table
                        columns = [
                            {'name': 'name', 'label': 'Model Name', 'field': 'name', 'align': 'left'},
                            {'name': 'path', 'label': 'Path', 'field': 'path', 'align': 'left'},
                            {'name': 'size', 'label': 'Size', 'field': 'size', 'align': 'right'},
                        ]
                        ui.table(columns=columns, rows=outputs, row_key='name').classes('w-full')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Refresh', on_click=update_outputs).props('icon=refresh')
                ui.button('Configure New Job', on_click=lambda: ui.navigate.to('/configure')).props('color=primary')
            
            # Initial load
            update_outputs()
