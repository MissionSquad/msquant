"""HuggingFace search dialog component for models and datasets."""
from typing import Callable, Optional, List
from nicegui import ui
from msquant.services import HuggingFaceService, HFSearchResult
import logging

logger = logging.getLogger(__name__)


class HFSearchDialog:
    """Dialog for searching HuggingFace models or datasets."""

    def __init__(
        self,
        hf_service: HuggingFaceService,
        search_type: str,
        on_select: Callable[[str], None],
        title: Optional[str] = None
    ):
        """
        Initialize the search dialog.

        Args:
            hf_service: HuggingFace service instance
            search_type: Type of search - 'model' or 'dataset'
            on_select: Callback function when an item is selected, receives the item ID
            title: Optional custom title for the dialog
        """
        if search_type not in ['model', 'dataset']:
            raise ValueError(f"search_type must be 'model' or 'dataset', got {search_type}")

        self.hf_service = hf_service
        self.search_type = search_type
        self.on_select = on_select
        self.title = title or f"Search HuggingFace {search_type.capitalize()}s"

        self.dialog: ui.dialog
        self.search_input: ui.input
        self.results_container: ui.column
        self.loading_spinner: ui.spinner
        self.error_label: ui.label
        self.sort_select: ui.select
        self.direction_select: ui.select
        self.search_results: List[HFSearchResult] = []

    def show(self):
        """Show the search dialog."""
        self.dialog = ui.dialog().props('maximized')

        with self.dialog, ui.card().classes('w-full h-full flex flex-col'):
            # Header with title and close button
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label(self.title).classes('text-3xl font-bold')
                ui.button(icon='close', on_click=self.dialog.close).props('flat round')

            # Search input and controls
            with ui.row().classes('w-full gap-4 mb-4'):
                self.search_input = ui.input(
                    placeholder=f'Search for {self.search_type}s...',
                    on_change=lambda: None  # We'll use the search button
                ).classes('flex-1').props('outlined clearable')

                # Bind Enter key to search
                self.search_input.on('keydown.enter', self._perform_search)

                ui.button('Search', on_click=self._perform_search).props('color=primary')

            # Sort options
            with ui.row().classes('w-full gap-4 mb-4'):
                ui.label('Sort by:').classes('self-center')
                self.sort_select = ui.select(
                    options=['downloads', 'likes', 'trending', 'modified', 'created'],
                    value='downloads',
                    label='Sort'
                ).classes('w-48')

                self.direction_select = ui.select(
                    options=[
                        {'label': 'Descending', 'value': 'desc'},
                        {'label': 'Ascending', 'value': 'asc'}
                    ],
                    value='desc',
                    label='Direction'
                ).classes('w-48').props('emit-value map-options')

            # Error message container
            self.error_label = ui.label('').classes('text-red-500 mb-2')
            self.error_label.set_visibility(False)

            # Loading spinner
            with ui.row().classes('w-full justify-center'):
                self.loading_spinner = ui.spinner(size='lg')
                self.loading_spinner.set_visibility(False)

            # Results container with scrolling
            with ui.scroll_area().classes('w-full flex-1'):
                self.results_container = ui.column().classes('w-full gap-4')

        self.dialog.open()

        # Perform initial search with empty query to show popular items
        self._perform_search()

    def _perform_search(self) -> None:
        """Perform the search based on current input."""
        query = self.search_input.value.strip() if self.search_input.value else ""
        sort = str(self.sort_select.value) if self.sort_select.value else 'downloads'
        # Convert string direction to integer: 'desc' -> -1, 'asc' -> 1
        direction_str = str(self.direction_select.value) if self.direction_select.value else 'desc'
        direction = -1 if direction_str == 'desc' else 1

        # Clear previous results and errors
        self.results_container.clear()
        self.error_label.set_text('')
        self.error_label.set_visibility(False)
        self.loading_spinner.set_visibility(True)

        try:
            # Perform search
            if self.search_type == 'model':
                self.search_results = self.hf_service.search_models(
                    query=query,
                    limit=20,
                    sort=sort,
                    direction=direction
                )
            else:  # dataset
                self.search_results = self.hf_service.search_datasets(
                    query=query,
                    limit=20,
                    sort=sort,
                    direction=direction
                )

            # Display results
            with self.results_container:
                if not self.search_results:
                    ui.label('No results found').classes('text-xl text-gray-500 text-center py-8')
                else:
                    ui.label(f'Found {len(self.search_results)} results').classes('text-lg font-semibold mb-2')

                    for result in self.search_results:
                        self._create_result_card(result)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.error_label.set_text(f'Search failed: {str(e)}')
            self.error_label.set_visibility(True)

        finally:
            self.loading_spinner.set_visibility(False)

    def _create_result_card(self, result: HFSearchResult):
        """Create a card for a single search result."""
        with ui.card().classes('w-full p-4 hover:shadow-lg cursor-pointer transition-shadow'):
            with ui.row().classes('w-full items-start justify-between gap-4'):
                # Left side - main info
                with ui.column().classes('flex-1 gap-2'):
                    # Title with ID
                    with ui.row().classes('items-center gap-2'):
                        ui.label(result.id).classes('text-xl font-bold')
                        if result.author:
                            ui.label(f'by {result.author}').classes('text-gray-600')

                    # Tags (show first 5)
                    if result.tags:
                        with ui.row().classes('gap-2 flex-wrap'):
                            for tag in result.tags[:5]:
                                ui.label(tag).classes('px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm')
                            if len(result.tags) > 5:
                                ui.label(f'+{len(result.tags) - 5} more').classes('px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm')

                    # Additional info
                    with ui.row().classes('gap-4 text-sm text-gray-600'):
                        if result.downloads is not None:
                            ui.label(f'↓ {result.downloads:,} downloads')
                        if result.likes is not None:
                            ui.label(f'❤ {result.likes:,} likes')
                        if result.library_name:
                            ui.label(f'📚 {result.library_name}')
                        if result.pipeline_tag:
                            ui.label(f'🏷 {result.pipeline_tag}')

                # Right side - action buttons
                with ui.column().classes('gap-2'):
                    ui.button(
                        'Select',
                        on_click=lambda e=None, r=result: self._select_item(r)
                    ).props('color=primary')

                    ui.button(
                        'View Details',
                        on_click=lambda e=None, r=result: self._show_details(r)
                    ).props('outline')

                    # Link to HuggingFace
                    hub_url = result.get_hub_url(self.search_type)
                    ui.link(
                        'Open in HF',
                        hub_url,
                        new_tab=True
                    ).classes('text-blue-600 underline text-sm')

    def _select_item(self, result: HFSearchResult):
        """Handle item selection."""
        try:
            self.on_select(result.id)
            self.dialog.close()
            ui.notify(f'Selected: {result.id}', type='positive')
        except Exception as e:
            logger.error(f"Selection failed: {e}")
            ui.notify(f'Failed to select item: {str(e)}', type='negative')

    def _show_details(self, result: HFSearchResult) -> None:
        """Show detailed information about an item."""
        details_dialog = ui.dialog().props('maximized')

        with details_dialog, ui.card().classes('w-full h-full flex flex-col overflow-auto'):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label(f'{self.search_type.capitalize()} Details').classes('text-3xl font-bold')
                ui.button(icon='close', on_click=details_dialog.close).props('flat round')

            # Loading state
            loading = ui.spinner(size='lg')

            try:
                # Fetch detailed info
                if self.search_type == 'model':
                    details = self.hf_service.get_model_details(result.id)
                else:
                    details = self.hf_service.get_dataset_details(result.id)

                loading.set_visibility(False)

                # Display details
                with ui.column().classes('w-full gap-4'):
                    # ID and basic info
                    ui.label(details['id']).classes('text-2xl font-bold')

                    if details.get('author'):
                        with ui.row().classes('gap-2'):
                            ui.label('Author:').classes('font-semibold')
                            ui.label(details['author'])

                    # Description
                    if details.get('description'):
                        ui.separator()
                        ui.label('Description').classes('text-xl font-bold')
                        ui.markdown(details['description']).classes('prose max-w-none')
                    else:
                        ui.label('No description available').classes('text-gray-500 italic')

                    # Stats
                    ui.separator()
                    ui.label('Statistics').classes('text-xl font-bold')
                    with ui.grid(columns=2).classes('gap-4 w-full max-w-2xl'):
                        ui.label('Downloads:').classes('font-semibold')
                        ui.label(f"{details.get('downloads', 0):,}")

                        ui.label('Likes:').classes('font-semibold')
                        ui.label(f"{details.get('likes', 0):,}")

                        if details.get('library_name'):
                            ui.label('Library:').classes('font-semibold')
                            ui.label(details['library_name'])

                        if details.get('pipeline_tag'):
                            ui.label('Pipeline:').classes('font-semibold')
                            ui.label(details['pipeline_tag'])

                        ui.label('Last Modified:').classes('font-semibold')
                        ui.label(str(details.get('last_modified', 'N/A')))

                    # Tags
                    if details.get('tags'):
                        ui.separator()
                        ui.label('Tags').classes('text-xl font-bold')
                        with ui.row().classes('gap-2 flex-wrap'):
                            for tag in details['tags']:
                                ui.label(tag).classes('px-3 py-1 bg-blue-100 text-blue-800 rounded')

                    # Actions
                    ui.separator()
                    with ui.row().classes('gap-4'):
                        ui.button(
                            'Select This',
                            on_click=lambda: [self._select_item(result), details_dialog.close()]
                        ).props('color=primary size=lg')

                        hub_url = result.get_hub_url(self.search_type)
                        ui.link(
                            'Open in HuggingFace',
                            hub_url,
                            new_tab=True
                        ).classes('text-blue-600 underline text-lg')

            except Exception as e:
                loading.set_visibility(False)
                logger.error(f"Failed to load details: {e}")
                ui.label(f'Failed to load details: {str(e)}').classes('text-red-500 text-xl')

        details_dialog.open()
