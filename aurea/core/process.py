"""
aurea.core.process — Unified, robust command execution engine.
"""

import subprocess
import time
from typing import Generator
from aurea.core import log, platform_info


class CommandRunner:
    """Consolidated, highly resilient process execution system with cross-platform fallbacks."""

    @staticmethod
    def run(command: list[str], timeout: float = 10.0, shell: bool = False) -> subprocess.CompletedProcess | None:
        """
        Executes a subprocess safely, capturing stdout/stderr and handling timeouts.
        Logs commands and execution failures to the diagnostic log subsystem.
        """
        # Cross-platform utility mapping
        cmd = CommandRunner._resolve_command(command)
        log.debug("Executing native command: %s (timeout=%.1fs)", " ".join(cmd), timeout)
        
        try:
            from aurea.core.ui import verbose
            verbose(f"Subprocesso nativo disparado: {' '.join(cmd)} (Timeout: {timeout}s)")
        except Exception:
            pass
        
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="ignore",
                timeout=timeout,
                shell=shell
            )
            if res.returncode != 0:
                log.warning("Command '%s' exited with code %d. Stderr: %s", cmd[0], res.returncode, res.stderr.strip())
                try:
                    verbose(f"Subprocesso finalizado com erro (Código: {res.returncode})")
                except Exception:
                    pass
            else:
                try:
                    verbose(f"Subprocesso concluído com sucesso (Código: 0). Retornou {len(res.stdout or '')} bytes de dados.")
                except Exception:
                    pass
            return res
        except subprocess.TimeoutExpired as e:
            log.error("Command timed out: %s (limit %.1fs)", " ".join(cmd), timeout)
            try:
                from aurea.core.ui import verbose
                verbose(f"ERRO: Tempo limite (Timeout) de {timeout}s expirado para o comando.")
            except Exception:
                pass
            return None
        except Exception as e:
            log.error("Failed to execute command '%s': %s", cmd[0], e)
            try:
                from aurea.core.ui import verbose
                verbose(f"ERRO: Falha ao invocar comando do sistema operacional: {e}")
            except Exception:
                pass
            return None

    @staticmethod
    def run_stream(command: list[str], timeout: float = 60.0) -> Generator[str, None, None]:
        """
        Executes a command and streams stdout/stderr line-by-line in real-time.
        Yields each line and handles timeouts/clean termination safely.
        """
        cmd = CommandRunner._resolve_command(command)
        log.debug("Streaming native command: %s (timeout=%.1fs)", " ".join(cmd), timeout)
        
        start_time = time.time()
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="ignore",
                bufsize=1
            )
            
            while True:
                # Check for timeout limit
                if time.time() - start_time > timeout:
                    log.error("Streaming command '%s' exceeded timeout limit of %.1fs. Terminating.", cmd[0], timeout)
                    process.terminate()
                    break
                
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    yield line
                    
            process.wait(timeout=2.0)
        except Exception as e:
            log.error("Streaming command failed for '%s': %s", cmd[0], e)
            yield f"Erro ao executar comando: {e}\n"

    @staticmethod
    def _resolve_command(command: list[str]) -> list[str]:
        """Auto-resolves binary names and fallbacks depending on OS."""
        if not command:
            return command
            
        binary = command[0].lower()
        
        # 1. ss and netstat fallback handling on Linux
        if binary == "ss" and not platform_info.is_windows():
            # Check if 'ss' executable is available
            import shutil
            if not shutil.which("ss"):
                # Fallback to netstat if ss is missing
                log.warning("'ss' utility not found. Falling back to 'netstat'.")
                if len(command) > 1 and "tuna" in command[1]:
                    return ["netstat", "-tuln"]
                return ["netstat", "-an"]
                
        # 2. Windows specific path resolutions or shell requirements
        if platform_info.is_windows():
            if binary in ("netstat", "ping", "arp"):
                # Ensure they execute directly without issues
                pass
                
        return command
