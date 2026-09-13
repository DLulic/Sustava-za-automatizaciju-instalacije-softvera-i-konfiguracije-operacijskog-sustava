import subprocess
import ctypes
import sys
import os
import tempfile
import time


def run_command(cmd, shell=True, timeout=None, require_admin=False, **kwargs):
    """
    Run a command, optionally elevating to admin if required.
    
    Args:
        cmd: Command string or list
        shell: Whether to use shell execution
        timeout: Timeout in seconds
        require_admin: If True, re-launch with admin privileges if not already admin
        **kwargs: Additional arguments for subprocess.run
    
    Returns:
        subprocess.CompletedProcess or None if elevation requested
    """
    if require_admin and not _is_admin():
        return _run_with_elevation(cmd, shell, timeout, **kwargs)
    
    return subprocess.run(cmd, shell=shell, timeout=timeout, **kwargs)


def _is_admin():
    """Check if current process is running as administrator."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _run_with_elevation(cmd, shell, timeout, **kwargs):
    """
    Run command with admin privileges by launching a temporary script elevated.
    Returns CompletedProcess with captured output.
    """
    python_exe = sys.executable
    
    # Create a temporary script that runs the command and writes output to files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as script_f:
        script_path = script_f.name
        script_f.write('# -*- coding: utf-8 -*-\n')
        script_f.write('import subprocess, sys, os\n')
        script_f.write('import json\n')
        script_f.write('\n')
        script_f.write('cmd = ' + repr(cmd) + '\n')
        script_f.write('shell = ' + repr(shell) + '\n')
        script_f.write('timeout = ' + repr(timeout) + '\n')
        script_f.write('\n')
        script_f.write('try:\n')
        script_f.write('    result = subprocess.run(cmd, shell=shell, timeout=timeout, capture_output=True, text=True)\n')
        script_f.write('    output = {\n')
        script_f.write('        "returncode": result.returncode,\n')
        script_f.write('        "stdout": result.stdout,\n')
        script_f.write('        "stderr": result.stderr,\n')
        script_f.write('        "cmd": str(cmd)\n')
        script_f.write('    }\n')
        script_f.write('except Exception as e:\n')
        script_f.write('    output = {"returncode": -1, "stdout": "", "stderr": str(e), "cmd": str(cmd)}\n')
        script_f.write('\n')
        script_f.write('output_path = os.path.join(os.path.dirname(__file__), ".subprocess_output.tmp")\n')
        script_f.write('with open(output_path, "w", encoding="utf-8") as f:\n')
        script_f.write('    json.dump(output, f, ensure_ascii=False)\n')
    
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", python_exe, f'"{script_path}"', os.getcwd(), 1
        )
        
        # Wait for elevated process to complete (poll for output file)
        output_path = os.path.join(os.path.dirname(script_path), ".subprocess_output.tmp")
        start_time = time.time()
        while not os.path.exists(output_path):
            if time.time() - start_time > (timeout or 600):
                break
            time.sleep(0.5)
        
        # Read output
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
                completed = subprocess.CompletedProcess(
                    args=output_data.get("cmd", cmd),
                    returncode=output_data.get("returncode", -1),
                    stdout=output_data.get("stdout", ""),
                    stderr=output_data.get("stderr", "")
                )
                return completed
            except Exception:
                pass
            finally:
                try:
                    os.unlink(output_path)
                except:
                    pass
        
        return None
        
    except Exception as e:
        return subprocess.CompletedProcess(
            args=cmd if isinstance(cmd, str) else cmd,
            returncode=-1,
            stdout="",
            stderr=str(e)
        )
    finally:
        try:
            os.unlink(script_path)
        except:
            pass
