"""Background job orchestration for quantization tasks."""
import json
import os
import signal
import subprocess
import tempfile
import threading
from typing import Optional, Callable, List
from collections import deque
from enum import Enum

from msquant.core.quantizer import QuantizationConfig


class JobStatus(Enum):
    """Job status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobService:
    """Manages background quantization jobs via subprocess."""
    
    def __init__(self, max_log_lines: int = 1000):
        """
        Initialize job service.
        
        Args:
            max_log_lines: Maximum number of log lines to keep in memory
        """
        self.max_log_lines = max_log_lines
        self.status = JobStatus.IDLE
        self.current_job: Optional[threading.Thread] = None
        self.logs: deque = deque(maxlen=max_log_lines)
        self.result: Optional[str] = None
        self.error: Optional[str] = None
        self._lock = threading.Lock()
        self._cancel_flag = False
        self._proc: Optional[subprocess.Popen] = None
    
    def start_job(self, config: QuantizationConfig) -> bool:
        """
        Start a quantization job.
        
        Args:
            config: QuantizationConfig instance
            
        Returns:
            True if job started, False if already running
        """
        with self._lock:
            if self.status == JobStatus.RUNNING:
                return False
            
            # Reset state
            self.logs.clear()
            self.result = None
            self.error = None
            self._cancel_flag = False
            self._proc = None
            self.status = JobStatus.RUNNING
            
            # Start job thread (manages subprocess)
            self.current_job = threading.Thread(
                target=self._run_job,
                args=(config,),
                daemon=True
            )
            self.current_job.start()
            return True
    
    def _run_job(self, config: QuantizationConfig):
        """Run the quantization job in a subprocess."""
        config_file = None
        try:
            # Serialize config to temporary file
            fd, config_file = tempfile.mkstemp(prefix="msq_config_", suffix=".json", text=True)
            with os.fdopen(fd, "w") as f:
                json.dump(config.__dict__, f)
            
            # Check for cancellation before starting
            if self._cancel_flag:
                with self._lock:
                    self.status = JobStatus.CANCELLED
                return
            
            # Start subprocess in its own process group
            # This allows us to kill the entire process tree
            self._proc = subprocess.Popen(
                ["python", "-m", "msquant.cli.quantize_run", "--config", config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                preexec_fn=os.setsid if os.name != 'nt' else None,  # Linux: new process group
            )
            
            # Stream logs from subprocess
            def _pump_logs():
                """Read subprocess stdout and pump to logs."""
                if not self._proc or not self._proc.stdout:
                    return
                
                for line in self._proc.stdout:
                    line = line.rstrip("\n")
                    
                    # Check for result marker
                    if line.startswith("__RESULT__:"):
                        result_json = line[len("__RESULT__:"):]
                        try:
                            result_data = json.loads(result_json)
                            with self._lock:
                                if result_data.get("status") == "success":
                                    self.result = result_data.get("output_dir")
                                elif result_data.get("status") == "error":
                                    self.error = result_data.get("message", "Unknown error")
                        except json.JSONDecodeError:
                            pass
                    else:
                        # Regular log line
                        with self._lock:
                            self.logs.append(line)
            
            log_thread = threading.Thread(target=_pump_logs, daemon=True)
            log_thread.start()
            
            # Wait for subprocess to complete
            return_code = self._proc.wait()
            
            # Wait for log thread to finish reading
            log_thread.join(timeout=2.0)
            
            # Update final status
            with self._lock:
                if self._cancel_flag:
                    self.status = JobStatus.CANCELLED
                elif return_code == 0:
                    self.status = JobStatus.COMPLETED
                else:
                    self.status = JobStatus.FAILED
                    if not self.error:
                        self.error = f"Process exited with code {return_code}"
                        
        except Exception as e:
            with self._lock:
                self.status = JobStatus.FAILED
                self.error = str(e)
        finally:
            # Cleanup
            if config_file and os.path.exists(config_file):
                try:
                    os.remove(config_file)
                except Exception:
                    pass
            self._proc = None
    
    def cancel_job(self):
        """Request job cancellation by terminating the subprocess."""
        with self._lock:
            if self.status != JobStatus.RUNNING:
                return
            
            self._cancel_flag = True
            proc = self._proc
        
        # Terminate the process group if subprocess is running
        if proc and proc.poll() is None:
            try:
                if os.name != 'nt':
                    # Linux: kill process group
                    os.killpg(proc.pid, signal.SIGTERM)
                    
                    # Wait for graceful termination
                    try:
                        proc.wait(timeout=10.0)
                    except subprocess.TimeoutExpired:
                        # Force kill if still running
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait(timeout=2.0)
                else:
                    # Windows: terminate process
                    proc.terminate()
                    proc.wait(timeout=10.0)
                    
            except (ProcessLookupError, OSError):
                # Process already terminated
                pass
            except Exception as e:
                with self._lock:
                    self.logs.append(f"Error during cancellation: {str(e)}")
    
    def get_status(self) -> JobStatus:
        """Get current job status."""
        with self._lock:
            return self.status
    
    def get_logs(self, last_n: Optional[int] = None) -> List[str]:
        """
        Get job logs.
        
        Args:
            last_n: Number of most recent lines to return (None for all)
            
        Returns:
            List of log lines
        """
        with self._lock:
            if last_n is None:
                return list(self.logs)
            return list(self.logs)[-last_n:]
    
    def get_result(self) -> Optional[str]:
        """Get job result if completed."""
        with self._lock:
            return self.result
    
    def get_error(self) -> Optional[str]:
        """Get job error if failed."""
        with self._lock:
            return self.error
