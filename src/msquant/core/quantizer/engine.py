"""
Unified quantization engine for MSQuant.
Wraps AWQ and NVFP4 quantization methods with a consistent interface.
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, Optional, Callable
import subprocess

import torch
from llmcompressor import oneshot
from llmcompressor.modifiers.awq import AWQModifier
from llmcompressor.modifiers.quantization import QuantizationModifier

from .config import QuantizationConfig


class QuantizationLogger:
    """Thread-safe logger with callback support for streaming logs."""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback
    
    def log(self, level: str, msg: str, payload: Optional[Dict] = None):
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} | {level.upper():5} | {msg}"
        
        if self.callback:
            self.callback(line)
        else:
            print(line, flush=True)
        
        if payload is not None:
            payload_str = json.dumps(payload, indent=2, sort_keys=True)
            if self.callback:
                self.callback(payload_str)
            else:
                print(payload_str, flush=True)
    
    def error(self, msg: str, payload: Optional[Dict] = None):
        self.log("ERROR", msg, payload)
    
    def info(self, msg: str, payload: Optional[Dict] = None):
        self.log("INFO", msg, payload)
    
    def warning(self, msg: str, payload: Optional[Dict] = None):
        self.log("WARN", msg, payload)


def nvidia_smi_query():
    """Query GPU information via nvidia-smi."""
    try:
        cmd = [
            "bash",
            "-lc",
            "nvidia-smi --query-gpu=index,name,memory.total,driver_version,compute_cap --format=csv,noheader"
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        gpus = []
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                gpus.append({
                    "index": int(parts[0]),
                    "name": parts[1],
                    "total_mem": parts[2],
                    "driver": parts[3],
                    "cc": parts[4],
                })
        return gpus
    except Exception:
        return []


def summarize_paths(hf_home: str, hf_datasets_cache: str):
    """Summarize disk usage of cache directories."""
    def du(path):
        try:
            out = subprocess.check_output(
                ["bash", "-lc", f"du -sh {path} 2>/dev/null | cut -f1"],
                text=True
            ).strip()
            return out or "0"
        except Exception:
            return "n/a"
    
    return {
        "HF_HOME": {"exists": os.path.isdir(hf_home), "size": du(hf_home)},
        "HF_DATASETS_CACHE": {"exists": os.path.isdir(hf_datasets_cache), "size": du(hf_datasets_cache)},
    }


class AWQQuantizer:
    """AWQ quantization handler."""
    
    @staticmethod
    def build_recipe(config: QuantizationConfig):
        """Build AWQ recipe."""
        config_groups = {
            "group_0": {
                "targets": ["Linear"],
                "input_activations": None,
                "output_activations": None,
                "weights": {
                    "num_bits": config.w_bit,
                    "type": "int",
                    "symmetric": config.zero_point,
                    "strategy": "group",
                    "group_size": config.group_size,
                },
            }
        }
        
        return [
            AWQModifier(
                config_groups=config_groups,  # type: ignore
                ignore=["lm_head"],
            ),
        ]
    
    @staticmethod
    def run(config: QuantizationConfig, logger: QuantizationLogger):
        """Run AWQ quantization."""
        recipe = AWQQuantizer.build_recipe(config)
        
        logger.info("Quant config:", {
            "quant_method": "awq",
            "w_bit": config.w_bit,
            "group_size": config.group_size,
            "zero_point": config.zero_point,
            "targets": ["Linear"],
        })
        
        oneshot_kwargs = {
            "model": config.model_id,
            "dataset": config.calib_dataset,
            "recipe": recipe,
            "output_dir": config.out_dir,
            "max_seq_length": config.max_seq_length,
            "num_calibration_samples": config.max_calib_samples,
        }
        
        if config.calib_config:
            oneshot_kwargs["dataset_config_name"] = config.calib_config
        
        if config.calib_split:
            oneshot_kwargs["dataset_split"] = config.calib_split
        
        logger.info("Starting LLM-Compressor oneshot() with AWQ", {
            "model": oneshot_kwargs["model"],
            "dataset": oneshot_kwargs["dataset"],
            "output_dir": oneshot_kwargs["output_dir"],
            "max_seq_length": oneshot_kwargs["max_seq_length"],
            "num_calibration_samples": oneshot_kwargs["num_calibration_samples"],
        })
        
        t0 = time.time()
        oneshot(**oneshot_kwargs)
        dt = time.time() - t0
        
        logger.info(f"Completed. Saved quantized checkpoint to {config.out_dir} in {dt:.1f}s")
        return config.out_dir


class NVFP4Quantizer:
    """NVFP4 quantization handler."""
    
    @staticmethod
    def build_recipe(config: QuantizationConfig):
        """Build NVFP4 recipe."""
        config_groups = {
            "group_0": {
                "targets": ["Linear"],
                "input_activations": {
                    "num_bits": 4 if config.act_scheme == "fp4" else 8,
                    "type": "float",
                    "strategy": "tensor",
                },
                "weights": {
                    "num_bits": 4 if config.w_scheme == "fp4" else 8,
                    "type": "float",
                    "strategy": "tensor",
                },
            }
        }
        
        return [
            QuantizationModifier(
                config_groups=config_groups,  # type: ignore
                ignore=["lm_head"],
            ),
        ]
    
    @staticmethod
    def run(config: QuantizationConfig, logger: QuantizationLogger):
        """Run NVFP4 quantization."""
        recipe = NVFP4Quantizer.build_recipe(config)
        
        logger.info("Quant config:", {
            "quant_method": "fp4",
            "act_scheme": config.act_scheme,
            "w_scheme": config.w_scheme,
            "non_uniform": config.non_uniform,
            "mix_fp8": config.mix_fp8,
            "targets": ["Linear"],
        })
        
        oneshot_kwargs = {
            "model": config.model_id,
            "dataset": config.calib_dataset,
            "recipe": recipe,
            "output_dir": config.out_dir,
            "max_seq_length": config.max_seq_length,
            "num_calibration_samples": config.max_calib_samples,
        }
        
        if config.calib_config:
            oneshot_kwargs["dataset_config_name"] = config.calib_config
        
        if config.calib_split:
            oneshot_kwargs["dataset_split"] = config.calib_split
        
        logger.info("Starting LLM-Compressor oneshot() with FP4 quantization", {
            "model": oneshot_kwargs["model"],
            "dataset": oneshot_kwargs["dataset"],
            "output_dir": oneshot_kwargs["output_dir"],
            "max_seq_length": oneshot_kwargs["max_seq_length"],
            "num_calibration_samples": oneshot_kwargs["num_calibration_samples"],
        })
        
        t0 = time.time()
        oneshot(**oneshot_kwargs)
        dt = time.time() - t0
        
        logger.info(f"Completed. Saved quantized checkpoint to {config.out_dir} in {dt:.1f}s")
        return config.out_dir


def quantize(config: QuantizationConfig, log_callback: Optional[Callable[[str], None]] = None):
    """
    Main quantization entry point.
    
    Args:
        config: QuantizationConfig instance
        log_callback: Optional callback for streaming logs
    
    Returns:
        Output directory path
    
    Raises:
        Exception on quantization failure
    """
    logger = QuantizationLogger(callback=log_callback)
    
    try:
        # Validate config
        config.validate()
        
        # Log runtime info
        logger.info("Runtime info:", {
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "torch": torch.__version__,
            "llmcompressor": __import__("llmcompressor").__version__,
            "gpus": nvidia_smi_query(),
            "config": {
                "model_id": config.model_id,
                "quant_method": config.quant_method,
                "output_format": config.output_format,
                "output_dir": config.out_dir,
                "calib_dataset": config.calib_dataset,
                "calib_config": config.calib_config,
                "max_calib_samples": config.max_calib_samples,
                "max_seq_length": config.max_seq_length,
            },
            "cache_info": summarize_paths(config.hf_home, config.hf_datasets_cache),
        })
        
        # Route to appropriate quantizer
        if config.quant_method == "awq":
            output_dir = AWQQuantizer.run(config, logger)
        elif config.quant_method == "nvfp4":
            output_dir = NVFP4Quantizer.run(config, logger)
        else:
            raise ValueError(f"Unsupported quantization method: {config.quant_method}")
        
        logger.info(f"Quantization complete! Output saved to: {output_dir}")
        logger.info(f"Next step: load in vLLM, e.g., `vllm serve {output_dir} --dtype float16`")
        
        return output_dir
        
    except Exception:
        logger.error("Quantization failed:")
        logger.error(traceback.format_exc())
        raise
