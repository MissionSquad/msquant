"""Quantization configuration."""
from typing import Optional


class QuantizationConfig:
    """Configuration for quantization job."""
    
    def __init__(
        self,
        model_id: str,
        quant_method: str,
        output_format: str,
        calib_dataset: str,
        calib_config: Optional[str] = None,
        calib_split: Optional[str] = None,
        max_calib_samples: int = 256,
        max_seq_length: int = 2048,
        # AWQ params
        w_bit: int = 4,
        group_size: int = 128,
        zero_point: bool = True,
        # NVFP4 params
        act_scheme: str = "fp4",
        w_scheme: str = "fp4",
        non_uniform: bool = False,
        mix_fp8: bool = False,
        # Paths
        hf_home: str = "/workspace/hf",
        hf_datasets_cache: str = "/workspace/hf/datasets",
        out_dir: Optional[str] = None,
    ):
        self.model_id = model_id
        self.quant_method = quant_method.lower()
        self.output_format = output_format.lower()
        self.calib_dataset = calib_dataset
        self.calib_config = calib_config
        self.calib_split = calib_split
        self.max_calib_samples = int(max_calib_samples)
        self.max_seq_length = int(max_seq_length)
        
        # AWQ
        self.w_bit = w_bit
        self.group_size = group_size
        self.zero_point = zero_point
        
        # NVFP4
        self.act_scheme = act_scheme
        self.w_scheme = w_scheme
        self.non_uniform = non_uniform
        self.mix_fp8 = mix_fp8
        
        # Paths
        self.hf_home = hf_home
        self.hf_datasets_cache = hf_datasets_cache
        
        # Generate output directory
        safe_name = model_id.split("/")[-1].replace(":", "-")
        if out_dir:
            self.out_dir = out_dir
        else:
            method_suffix = self.quant_method.upper()
            format_suffix = "-safetensors" if self.output_format == "safetensors" else ""
            self.out_dir = f"/workspace/out/{safe_name}-{method_suffix}{format_suffix}"
    
    def validate(self):
        """Validate configuration."""
        if not self.model_id:
            raise ValueError("model_id is required")
        
        if self.quant_method not in ["awq", "nvfp4"]:
            raise ValueError(f"Invalid quant_method: {self.quant_method}")
        
        if self.output_format not in ["binary", "safetensors"]:
            raise ValueError(f"Invalid output_format: {self.output_format}")
        
        if self.quant_method == "awq":
            if self.w_bit not in [2, 3, 4, 5, 8]:
                raise ValueError(f"Invalid w_bit for AWQ: {self.w_bit}")
            if self.group_size <= 0:
                raise ValueError(f"Invalid group_size: {self.group_size}")
