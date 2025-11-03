"""
GPU Monitoring utilities for MSQuant.
Provides real-time GPU metrics similar to nvtop.
"""
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque


class GPUMetrics:
    """Stores metrics for a single GPU."""
    
    def __init__(
        self,
        index: int,
        name: str,
        utilization: float,
        memory_used: int,
        memory_total: int,
        temperature: float,
        power_draw: float,
        power_limit: float,
    ):
        self.index = index
        self.name = name
        self.utilization = utilization
        self.memory_used = memory_used
        self.memory_total = memory_total
        self.memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        self.temperature = temperature
        self.power_draw = power_draw
        self.power_limit = power_limit
        self.power_percent = (power_draw / power_limit * 100) if power_limit > 0 else 0
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "name": self.name,
            "utilization": self.utilization,
            "memory_used": self.memory_used,
            "memory_total": self.memory_total,
            "memory_percent": self.memory_percent,
            "temperature": self.temperature,
            "power_draw": self.power_draw,
            "power_limit": self.power_limit,
            "power_percent": self.power_percent,
            "timestamp": self.timestamp.isoformat(),
        }


class GPUMonitor:
    """Monitors GPU metrics over time."""
    
    def __init__(self, history_size: int = 60):
        """
        Initialize GPU monitor.
        
        Args:
            history_size: Number of historical samples to keep per GPU
        """
        self.history_size = history_size
        self.gpu_history: Dict[int, deque] = {}
    
    def query_gpus(self) -> List[GPUMetrics]:
        """
        Query current GPU metrics using nvidia-smi.
        
        Returns:
            List of GPUMetrics objects
        """
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit",
                "--format=csv,noheader,nounits"
            ]
            
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
            
            gpus = []
            for line in output.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 8:
                    try:
                        gpu = GPUMetrics(
                            index=int(parts[0]),
                            name=parts[1],
                            utilization=float(parts[2]),
                            memory_used=int(parts[3]),
                            memory_total=int(parts[4]),
                            temperature=float(parts[5]),
                            power_draw=float(parts[6]),
                            power_limit=float(parts[7]),
                        )
                        gpus.append(gpu)
                        
                        # Store in history
                        if gpu.index not in self.gpu_history:
                            self.gpu_history[gpu.index] = deque(maxlen=self.history_size)
                        self.gpu_history[gpu.index].append(gpu)
                        
                    except (ValueError, IndexError) as e:
                        continue
            
            return gpus
            
        except Exception as e:
            return []
    
    def get_history(self, gpu_index: int) -> List[GPUMetrics]:
        """
        Get historical metrics for a specific GPU.
        
        Args:
            gpu_index: GPU index
            
        Returns:
            List of historical GPUMetrics
        """
        return list(self.gpu_history.get(gpu_index, []))
    
    def format_summary(self, gpus: List[GPUMetrics]) -> str:
        """
        Format a text summary of GPU status.
        
        Args:
            gpus: List of GPUMetrics
            
        Returns:
            Formatted string
        """
        if not gpus:
            return "⚠️ No GPUs detected or nvidia-smi unavailable"
        
        lines = []
        for gpu in gpus:
            lines.append(f"**GPU {gpu.index}: {gpu.name}**")
            lines.append(f"- Utilization: {gpu.utilization:.1f}%")
            lines.append(f"- Memory: {gpu.memory_used} MB / {gpu.memory_total} MB ({gpu.memory_percent:.1f}%)")
            lines.append(f"- Temperature: {gpu.temperature:.1f}°C")
            lines.append(f"- Power: {gpu.power_draw:.1f}W / {gpu.power_limit:.1f}W ({gpu.power_percent:.1f}%)")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_chart_data(self, gpu_index: int, metric: str) -> tuple:
        """
        Get chart data for a specific metric.
        
        Args:
            gpu_index: GPU index
            metric: Metric name (utilization, memory_percent, temperature, power_draw)
            
        Returns:
            Tuple of (timestamps, values)
        """
        history = self.get_history(gpu_index)
        if not history:
            return [], []
        
        timestamps = [gpu.timestamp for gpu in history]
        
        if metric == "utilization":
            values = [gpu.utilization for gpu in history]
        elif metric == "memory_percent":
            values = [gpu.memory_percent for gpu in history]
        elif metric == "temperature":
            values = [gpu.temperature for gpu in history]
        elif metric == "power_draw":
            values = [gpu.power_draw for gpu in history]
        elif metric == "power_percent":
            values = [gpu.power_percent for gpu in history]
        else:
            values = []
        
        return timestamps, values


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"
