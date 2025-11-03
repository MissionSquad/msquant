"""Layout components for MSQuant application."""
from nicegui import ui


def create_header():
    """Create the application header with navigation."""
    with ui.header().classes('items-center justify-between'):
        ui.label('MSQuant').classes('text-2xl font-bold')
        
        with ui.row().classes('gap-4'):
            ui.link('Home', '/').classes('text-white no-underline')
            ui.link('Configure', '/configure').classes('text-white no-underline')
            ui.link('Monitor', '/monitor').classes('text-white no-underline')
            ui.link('Results', '/results').classes('text-white no-underline')
