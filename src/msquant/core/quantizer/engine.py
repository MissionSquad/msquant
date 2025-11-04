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
                    "symmetric": not config.zero_point,
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
            oneshot_kwargs["splits"] = {"calibration": config.calib_split}

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
            oneshot_kwargs["splits"] = {"calibration": config.calib_split}

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


class GGUFQuantizer:
    """GGUF quantization handler using llama.cpp."""

    @staticmethod
    def _check_llama_cpp_available():
        """Check if llama.cpp tools are available."""
        try:
            # Check if convert-hf-to-gguf.py is available
            result = subprocess.run(
                ["bash", "-lc", "which python"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                raise RuntimeError("Python not found in PATH")

            # Check if llama-quantize is available
            result = subprocess.run(
                ["bash", "-lc", "which llama-quantize"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "llama-quantize not found in PATH. "
                    "Please ensure llama.cpp is properly installed."
                )
            return True
        except Exception as e:
            raise RuntimeError(f"llama.cpp availability check failed: {e}") from e

    @staticmethod
    def _download_model(model_id: str, cache_dir: str, logger: QuantizationLogger) -> str:
        """Download HuggingFace model to local cache."""
        from huggingface_hub import snapshot_download
        from huggingface_hub.utils import (
            HfHubHTTPError,
            RepositoryNotFoundError,
            GatedRepoError,
            LocalEntryNotFoundError,
        )
        from requests.exceptions import ConnectionError, Timeout

        logger.info(f"Downloading model {model_id} to cache...")
        try:
            local_path = snapshot_download(
                repo_id=model_id,
                cache_dir=cache_dir,
                local_dir_use_symlinks=False
            )
            logger.info(f"Model downloaded to {local_path}")
            return local_path
        except RepositoryNotFoundError as e:
            raise RuntimeError(
                f"Model '{model_id}' not found on HuggingFace Hub. "
                f"Please verify the model ID is correct."
            ) from e
        except GatedRepoError as e:
            raise RuntimeError(
                f"Model '{model_id}' is gated and requires authentication. "
                f"Please log in with 'huggingface-cli login' and ensure you have access."
            ) from e
        except HfHubHTTPError as e:
            if e.response.status_code == 401:
                raise RuntimeError(
                    f"Authentication failed for model '{model_id}'. "
                    f"Please log in with 'huggingface-cli login'."
                ) from e
            elif e.response.status_code == 403:
                raise RuntimeError(
                    f"Access denied for model '{model_id}'. "
                    f"You may need to accept the model's license agreement on HuggingFace Hub."
                ) from e
            else:
                raise RuntimeError(
                    f"HTTP error {e.response.status_code} while downloading model '{model_id}': {e}"
                ) from e
        except (ConnectionError, Timeout) as e:
            raise RuntimeError(
                f"Network error while downloading model '{model_id}'. "
                f"Please check your internet connection and try again."
            ) from e
        except LocalEntryNotFoundError as e:
            raise RuntimeError(
                f"Model files not found for '{model_id}'. "
                f"The repository may be empty or misconfigured."
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to download model '{model_id}': {e}"
            ) from e

    @staticmethod
    def _convert_to_gguf_intermediate(
        model_path: str,
        output_file: str,
        intermediate_format: str,
        logger: QuantizationLogger
    ):
        """Convert HuggingFace model to intermediate GGUF format."""
        logger.info(f"Converting model to GGUF {intermediate_format} format...")

        # Find the convert-hf-to-gguf.py script
        convert_script = "/opt/llama.cpp/convert-hf-to-gguf.py"

        # Build the conversion command
        cmd = [
            "python",
            convert_script,
            model_path,
            "--outfile", output_file,
            "--outtype", intermediate_format
        ]

        logger.info(f"Running command: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Stream output
            if process.stdout:
                for line in process.stdout:
                    line = line.rstrip()
                    if line:
                        logger.info(f"[convert] {line}")

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Conversion failed with exit code {process.returncode}")

            logger.info(f"Conversion completed. Intermediate GGUF file: {output_file}")

        except Exception as e:
            raise RuntimeError(f"GGUF conversion failed: {e}") from e

    @staticmethod
    def _quantize_gguf(
        input_file: str,
        output_file: str,
        quant_type: str,
        intermediate_format: str,
        logger: QuantizationLogger
    ):
        """Quantize GGUF file to target precision."""
        logger.info(f"Quantizing GGUF to {quant_type}...")

        # Skip quantization if target format matches intermediate format
        if quant_type.upper() == intermediate_format.upper():
            logger.info(f"Target format {quant_type} matches intermediate format {intermediate_format}, skipping quantization")
            # Only copy if the filenames are different
            if input_file != output_file:
                import shutil
                shutil.copy2(input_file, output_file)
            return

        # Build the quantization command
        cmd = [
            "llama-quantize",
            input_file,
            output_file,
            quant_type
        ]

        logger.info(f"Running command: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Stream output
            if process.stdout:
                for line in process.stdout:
                    line = line.rstrip()
                    if line:
                        logger.info(f"[quantize] {line}")

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Quantization failed with exit code {process.returncode}")

            logger.info(f"Quantization completed. Output file: {output_file}")

        except Exception as e:
            raise RuntimeError(f"GGUF quantization failed: {e}") from e

    @staticmethod
    def run(config: QuantizationConfig, logger: QuantizationLogger):
        """Run GGUF quantization."""
        import os

        # Check if llama.cpp is available
        GGUFQuantizer._check_llama_cpp_available()

        logger.info("GGUF Quantization config:", {
            "quant_type": config.gguf_quant_type,
            "intermediate_format": config.gguf_intermediate_format,
            "model_id": config.model_id,
        })

        t0 = time.time()

        # Step 1: Download model from HuggingFace
        model_path = GGUFQuantizer._download_model(
            config.model_id,
            config.hf_home,
            logger
        )

        # Step 2: Convert to intermediate GGUF format
        os.makedirs(config.out_dir, exist_ok=True)
        safe_name = config.model_id.split("/")[-1].replace(":", "-")
        intermediate_file = os.path.join(
            config.out_dir,
            f"{safe_name}-{config.gguf_intermediate_format}.gguf"
        )

        GGUFQuantizer._convert_to_gguf_intermediate(
            model_path,
            intermediate_file,
            config.gguf_intermediate_format,
            logger
        )

        # Step 3: Quantize to target precision
        final_file = os.path.join(
            config.out_dir,
            f"{safe_name}-{config.gguf_quant_type}.gguf"
        )

        GGUFQuantizer._quantize_gguf(
            intermediate_file,
            final_file,
            config.gguf_quant_type,
            config.gguf_intermediate_format,
            logger
        )

        # Clean up intermediate file if different from final
        # Use os.path.samefile to handle case-insensitive filesystems
        try:
            if os.path.exists(intermediate_file) and os.path.exists(final_file):
                if not os.path.samefile(intermediate_file, final_file):
                    logger.info(f"Cleaning up intermediate file: {intermediate_file}")
                    os.remove(intermediate_file)
        except (OSError, ValueError):
            # If samefile fails, fall back to string comparison
            if intermediate_file != final_file and os.path.exists(intermediate_file):
                logger.info(f"Cleaning up intermediate file: {intermediate_file}")
                os.remove(intermediate_file)

        dt = time.time() - t0
        logger.info(f"Completed. Saved GGUF quantized model to {final_file} in {dt:.1f}s")

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
        elif config.quant_method == "gguf":
            output_dir = GGUFQuantizer.run(config, logger)
        else:
            raise ValueError(f"Unsupported quantization method: {config.quant_method}")
        
        logger.info(f"Quantization complete! Output saved to: {output_dir}")
        logger.info(f"Next step: load in vLLM, e.g., `vllm serve {output_dir} --dtype float16`")
        
        return output_dir
        
    except Exception:
        logger.error("Quantization failed:")
        logger.error(traceback.format_exc())
        raise
