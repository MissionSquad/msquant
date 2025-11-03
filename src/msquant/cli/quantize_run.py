"""CLI runner for quantization jobs.

This module is executed as a subprocess to enable robust job cancellation.
It deserializes configuration, runs quantization, and outputs logs to stdout.
"""
import argparse
import json
import sys

from msquant.core.quantizer import QuantizationConfig, quantize


def _log_printer(line: str) -> None:
    """Print log line to stdout with flush."""
    print(line, flush=True)


def main() -> int:
    """Main entry point for CLI quantization runner."""
    parser = argparse.ArgumentParser(description="Run quantization job from config file")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to JSON configuration file"
    )
    args = parser.parse_args()
    
    try:
        # Load configuration
        with open(args.config, "r") as f:
            config_dict = json.load(f)
        
        # Create config object
        config = QuantizationConfig(**config_dict)
        
        # Run quantization with stdout logging
        output_dir = quantize(config, log_callback=_log_printer)
        
        # Print result as JSON for parent to parse
        result = {"status": "success", "output_dir": output_dir}
        print(f"__RESULT__:{json.dumps(result)}", flush=True)
        
        return 0
        
    except Exception as e:
        # Print error for parent to capture
        error_result = {"status": "error", "message": str(e)}
        print(f"__RESULT__:{json.dumps(error_result)}", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
