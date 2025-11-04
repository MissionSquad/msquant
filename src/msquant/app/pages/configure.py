"""Configuration page for setting up quantization jobs."""
from nicegui import ui
from msquant.core.quantizer import QuantizationConfig
from msquant.services import JobService, StorageService


def create_configure_page(job_service: JobService, storage_service: StorageService):
    """Create the configuration page."""
    
    # Form state
    form_data = {
        'model_id': 'meta-llama/Llama-3.1-8B',
        'quant_method': 'awq',
        'output_format': 'binary',
        'calib_dataset': 'wikitext',
        'calib_config': 'wikitext-2-raw-v1',
        'calib_split': 'train',
        'max_calib_samples': 256,
        'max_seq_length': 2048,
        'w_bit': 4,
        'group_size': 128,
        'zero_point': True,
    }
    
    def start_quantization():
        """Start the quantization job."""
        try:
            config = QuantizationConfig(
                model_id=form_data['model_id'],
                quant_method=form_data['quant_method'],
                output_format=form_data['output_format'],
                calib_dataset=form_data['calib_dataset'],
                calib_config=form_data['calib_config'] if form_data['calib_config'] else None,
                calib_split=form_data['calib_split'] if form_data['calib_split'] else None,
                max_calib_samples=form_data['max_calib_samples'],
                max_seq_length=form_data['max_seq_length'],
                w_bit=form_data['w_bit'],
                group_size=form_data['group_size'],
                zero_point=form_data['zero_point'],
            )
            
            if job_service.start_job(config):
                ui.notify('Quantization job started!', type='positive')
                ui.navigate.to('/monitor')
            else:
                ui.notify('A job is already running', type='warning')
        except Exception as e:
            ui.notify(f'Error: {str(e)}', type='negative')
    
    with ui.column().classes('w-full p-8'):
        ui.label('Configure Quantization').classes('text-4xl font-bold mb-8')
        
        with ui.card().classes('w-full max-w-4xl'):
            with ui.column().classes('w-full gap-4'):
                # Model settings
                ui.label('Model Settings').classes('text-2xl font-bold')
                ui.input('Model ID', placeholder='e.g., meta-llama/Llama-3.1-8B').classes('w-full').bind_value(form_data, 'model_id')
                
                ui.separator()
                
                # Quantization method
                ui.label('Quantization Method').classes('text-2xl font-bold')
                with ui.row().classes('w-full gap-4'):
                    ui.radio(['awq', 'nvfp4'], value='awq').bind_value(form_data, 'quant_method').props('inline')
                
                ui.separator()
                
                # Calibration settings
                ui.label('Calibration Settings').classes('text-2xl font-bold')
                ui.input('Calibration Dataset', placeholder='e.g., wikitext').classes('w-full').bind_value(form_data, 'calib_dataset')
                ui.input('Dataset Config', placeholder='e.g., wikitext-2-raw-v1 (optional)').classes('w-full').bind_value(form_data, 'calib_config')
                ui.select(
                    ['train', 'test', 'validation', 'train[:512]', 'test[:512]'],
                    value='train',
                    label='Dataset Split'
                ).classes('w-full').bind_value(form_data, 'calib_split').props('use-input new-value-mode=add-unique clearable')

                with ui.row().classes('w-full gap-4'):
                    ui.select(
                        [128, 256, 512, 1024, 2048],
                        value=256,
                        label='Max Calibration Samples'
                    ).classes('flex-1').bind_value(form_data, 'max_calib_samples').props('use-input new-value-mode=add-unique')
                    ui.select(
                        [512, 1024, 2048, 4096, 8192],
                        value=2048,
                        label='Max Sequence Length'
                    ).classes('flex-1').bind_value(form_data, 'max_seq_length').props('use-input new-value-mode=add-unique')
                
                ui.separator()
                
                # AWQ-specific settings
                ui.label('AWQ Settings (only for AWQ method)').classes('text-2xl font-bold')
                with ui.row().classes('w-full gap-4'):
                    ui.select([2, 3, 4, 5, 8], value=4, label='Weight Bits').classes('flex-1').bind_value(form_data, 'w_bit')
                    ui.select(
                        [32, 64, 128, 256],
                        value=128,
                        label='Group Size'
                    ).classes('flex-1').bind_value(form_data, 'group_size').props('use-input new-value-mode=add-unique')
                ui.checkbox('Zero Point', value=True).bind_value(form_data, 'zero_point')
                
                ui.separator()
                
                # Actions
                with ui.row().classes('w-full gap-4 justify-end'):
                    ui.button('Start Quantization', on_click=start_quantization).props('color=primary size=lg')
                    ui.button('Monitor Jobs', on_click=lambda: ui.navigate.to('/monitor')).props('size=lg')
