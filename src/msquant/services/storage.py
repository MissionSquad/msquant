"""Storage and path management for MSQuant."""
import os
from typing import List, Dict, Optional
from pathlib import Path


class StorageService:
    """Manages storage paths and output directories."""
    
    def __init__(
        self,
        out_dir: str = "/workspace/out",
        hf_home: str = "/workspace/hf",
        hf_datasets_cache: str = "/workspace/hf/datasets",
    ):
        """
        Initialize storage service.
        
        Args:
            out_dir: Output directory for quantized models
            hf_home: HuggingFace home directory
            hf_datasets_cache: HuggingFace datasets cache directory
        """
        self.out_dir = Path(out_dir)
        self.hf_home = Path(hf_home)
        self.hf_datasets_cache = Path(hf_datasets_cache)
        
        # Create directories if they don't exist
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.hf_home.mkdir(parents=True, exist_ok=True)
        self.hf_datasets_cache.mkdir(parents=True, exist_ok=True)
    
    def list_outputs(self) -> List[Dict[str, str]]:
        """
        List all output directories.
        
        Returns:
            List of dicts with name, path, and size info
        """
        outputs = []
        
        if not self.out_dir.exists():
            return outputs
        
        for item in self.out_dir.iterdir():
            if item.is_dir():
                outputs.append({
                    "name": item.name,
                    "path": str(item),
                    "size": self._get_dir_size(item),
                })
        
        # Sort by modification time (newest first)
        outputs.sort(key=lambda x: os.path.getmtime(x["path"]), reverse=True)
        
        return outputs
    
    def _get_dir_size(self, path: Path) -> str:
        """
        Get human-readable directory size.
        
        Args:
            path: Directory path
            
        Returns:
            Size string (e.g., "1.5 GB")
        """
        try:
            total_size = sum(
                f.stat().st_size for f in path.rglob('*') if f.is_file()
            )
            return self._format_bytes(total_size)
        except Exception:
            return "Unknown"
    
    @staticmethod
    def _format_bytes(bytes_val: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"
    
    def get_cache_info(self) -> Dict[str, Dict[str, str]]:
        """
        Get cache directory information.
        
        Returns:
            Dict with cache info
        """
        return {
            "hf_home": {
                "path": str(self.hf_home),
                "exists": self.hf_home.exists(),
                "size": self._get_dir_size(self.hf_home) if self.hf_home.exists() else "0 B",
            },
            "hf_datasets_cache": {
                "path": str(self.hf_datasets_cache),
                "exists": self.hf_datasets_cache.exists(),
                "size": self._get_dir_size(self.hf_datasets_cache) if self.hf_datasets_cache.exists() else "0 B",
            },
        }
