import psutil
import subprocess
import os
import time
import signal
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import platform

@dataclass
class ProcessInfo:
    """Data class for process information"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_info: Dict[str, int]
    create_time: float
    exe: Optional[str]
    cmdline: List[str]
    username: Optional[str]

class ProcessManager:
    """
    Advanced process management system with AI-friendly interface
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.supported_operations = {
            'windows': ['list', 'start', 'stop', 'restart', 'kill', 'monitor', 'info'],
            'linux': ['list', 'start', 'stop', 'restart', 'kill', 'monitor', 'info'],
            'darwin': ['list', 'start', 'stop', 'restart', 'kill', 'monitor', 'info']
        }
    
    def get_running_processes(self, filter_name: str = None, 
                             sort_by: str = 'name') -> List[ProcessInfo]:
        """
        Get list of running processes
        
        Args:
            filter_name: Filter processes by name (partial match)
            sort_by: Sort by 'name', 'cpu', 'memory', or 'pid'
            
        Returns:
            List of ProcessInfo objects
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                           'memory_percent', 'memory_info', 'create_time',
                                           'exe', 'cmdline', 'username']):
                try:
                    proc_info = proc.info
                    
                    # Apply filter if specified
                    if filter_name and filter_name.lower() not in proc_info['name'].lower():
                        continue
                    
                    # Convert memory_info to dict if it exists
                    memory_info = proc_info['memory_info'] or {}
                    if hasattr(memory_info, '_asdict'):
                        memory_info = memory_info._asdict()
                    
                    process_info = ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'],
                        status=proc_info['status'],
                        cpu_percent=proc_info['cpu_percent'] or 0.0,
                        memory_percent=proc_info['memory_percent'] or 0.0,
                        memory_info=memory_info,
                        create_time=proc_info['create_time'],
                        exe=proc_info['exe'],
                        cmdline=proc_info['cmdline'] or [],
                        username=proc_info['username']
                    )
                    
                    processes.append(process_info)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        
        except Exception as e:
            raise RuntimeError(f"Error getting process list: {str(e)}")
        
        # Sort processes
        if sort_by == 'name':
            processes.sort(key=lambda x: x.name.lower())
        elif sort_by == 'cpu':
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x.memory_percent, reverse=True)
        elif sort_by == 'pid':
            processes.sort(key=lambda x: x.pid)
        
        return processes
    
    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """
        Get process information by PID
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessInfo object or None if not found
        """
        try:
            proc = psutil.Process(pid)
            
            memory_info = proc.memory_info()
            if hasattr(memory_info, '_asdict'):
                memory_info = memory_info._asdict()
            
            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                status=proc.status(),
                cpu_percent=proc.cpu_percent(),
                memory_percent=proc.memory_percent(),
                memory_info=memory_info,
                create_time=proc.create_time(),
                exe=proc.exe(),
                cmdline=proc.cmdline(),
                username=proc.username()
            )
        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
    
    def get_process_by_name(self, name: str, exact_match: bool = False) -> List[ProcessInfo]:
        """
        Get processes by name
        
        Args:
            name: Process name to search for
            exact_match: Whether to require exact name match
            
        Returns:
            List of matching ProcessInfo objects
        """
        processes = self.get_running_processes()
        
        if exact_match:
            return [p for p in processes if p.name.lower() == name.lower()]
        else:
            return [p for p in processes if name.lower() in p.name.lower()]
    
    def start_process(self, command: str, args: List[str] = None, 
                     working_dir: str = None, shell: bool = False) -> Dict[str, Any]:
        """
        Start a new process
        
        Args:
            command: Command to execute
            args: Additional arguments
            working_dir: Working directory for the process
            shell: Whether to run in shell
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Prepare command
            if args:
                full_command = [command] + args
            else:
                full_command = command
            
            # Start process
            if self.system == 'windows':
                # On Windows, use subprocess with proper handling
                proc = subprocess.Popen(
                    full_command,
                    shell=shell,
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                # On Unix-like systems
                proc = subprocess.Popen(
                    full_command,
                    shell=shell,
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid if not shell else None
                )
            
            # Get process info
            time.sleep(0.1)  # Give process time to start
            
            try:
                psutil_proc = psutil.Process(proc.pid)
                process_info = self.get_process_by_pid(proc.pid)
                
                return {
                    'success': True,
                    'message': f"Process started: {command}",
                    'pid': proc.pid,
                    'process_info': process_info,
                    'command': command,
                    'args': args or []
                }
            
            except psutil.NoSuchProcess:
                # Process might have exited immediately
                stdout, stderr = proc.communicate()
                return {
                    'success': False,
                    'message': f"Process exited immediately: {command}",
                    'pid': proc.pid,
                    'stdout': stdout,
                    'stderr': stderr,
                    'return_code': proc.returncode
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error starting process: {str(e)}",
                'command': command,
                'args': args or []
            }
    
    def stop_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """
        Stop a running process
        
        Args:
            pid: Process ID
            force: Whether to force kill the process
            
        Returns:
            Dictionary with operation result
        """
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            if force:
                # Force kill
                if self.system == 'windows':
                    proc.kill()
                else:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                method = "killed"
            else:
                # Graceful termination
                proc.terminate()
                method = "terminated"
                
                # Wait for process to terminate
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    # If graceful termination fails, force kill
                    proc.kill()
                    method = "killed (timeout)"
            
            return {
                'success': True,
                'message': f"Process {process_name} (PID: {pid}) {method}",
                'pid': pid,
                'name': process_name,
                'method': method
            }
        
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'message': f"Process not found: PID {pid}",
                'pid': pid
            }
        except psutil.AccessDenied:
            return {
                'success': False,
                'message': f"Access denied to process: PID {pid}",
                'pid': pid
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error stopping process: {str(e)}",
                'pid': pid
            }
    
    def restart_process(self, pid: int) -> Dict[str, Any]:
        """
        Restart a process
        
        Args:
            pid: Process ID to restart
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Get process info before stopping
            old_proc = psutil.Process(pid)
            process_name = old_proc.name()
            cmdline = old_proc.cmdline()
            working_dir = old_proc.cwd()
            
            # Stop the process
            stop_result = self.stop_process(pid)
            
            if not stop_result['success']:
                return stop_result
            
            # Wait a moment
            time.sleep(1)
            
            # Restart with same command line
            if cmdline:
                restart_result = self.start_process(
                    cmdline[0], 
                    cmdline[1:], 
                    working_dir=working_dir
                )
            else:
                restart_result = self.start_process(process_name, working_dir=working_dir)
            
            if restart_result['success']:
                restart_result['message'] = f"Process {process_name} restarted. New PID: {restart_result['pid']}"
            else:
                restart_result['message'] = f"Failed to restart process {process_name}: {restart_result['message']}"
            
            return restart_result
        
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'message': f"Process not found: PID {pid}",
                'pid': pid
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error restarting process: {str(e)}",
                'pid': pid
            }
    
    def monitor_process(self, pid: int, duration: int = 10, 
                       interval: float = 1.0) -> Dict[str, Any]:
        """
        Monitor a process over time
        
        Args:
            pid: Process ID to monitor
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds
            
        Returns:
            Dictionary with monitoring data
        """
        monitoring_data = {
            'pid': pid,
            'duration': duration,
            'interval': interval,
            'samples': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    cpu_percent = proc.cpu_percent()
                    memory_percent = proc.memory_percent()
                    memory_info = proc.memory_info()
                    
                    sample = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'memory_rss': memory_info.rss,
                        'memory_vms': memory_info.vms,
                        'status': proc.status()
                    }
                    
                    monitoring_data['samples'].append(sample)
                    
                    time.sleep(interval)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    monitoring_data['samples'].append({
                        'timestamp': datetime.now().isoformat(),
                        'error': 'Process no longer accessible'
                    })
                    break
            
            monitoring_data['end_time'] = datetime.now().isoformat()
            monitoring_data['process_name'] = process_name
            monitoring_data['sample_count'] = len(monitoring_data['samples'])
            
            # Calculate statistics
            if monitoring_data['samples']:
                cpu_values = [s.get('cpu_percent', 0) for s in monitoring_data['samples'] if 'cpu_percent' in s]
                memory_values = [s.get('memory_percent', 0) for s in monitoring_data['samples'] if 'memory_percent' in s]
                
                if cpu_values:
                    monitoring_data['cpu_stats'] = {
                        'avg': sum(cpu_values) / len(cpu_values),
                        'max': max(cpu_values),
                        'min': min(cpu_values)
                    }
                
                if memory_values:
                    monitoring_data['memory_stats'] = {
                        'avg': sum(memory_values) / len(memory_values),
                        'max': max(memory_values),
                        'min': min(memory_values)
                    }
            
            return {
                'success': True,
                'message': f"Monitoring completed for process {process_name} (PID: {pid})",
                'data': monitoring_data
            }
        
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'message': f"Process not found: PID {pid}",
                'pid': pid
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error monitoring process: {str(e)}",
                'pid': pid
            }
    
    def get_system_processes_summary(self) -> Dict[str, Any]:
        """
        Get summary of all system processes
        
        Returns:
            Dictionary with system process summary
        """
        try:
            processes = self.get_running_processes()
            
            # Calculate statistics
            total_processes = len(processes)
            running_processes = len([p for p in processes if p.status == 'running'])
            sleeping_processes = len([p for p in processes if p.status == 'sleeping'])
            
            # CPU and memory totals
            total_cpu = sum(p.cpu_percent for p in processes)
            total_memory = sum(p.memory_percent for p in processes)
            
            # Top processes by CPU and memory
            top_cpu = sorted(processes, key=lambda x: x.cpu_percent, reverse=True)[:5]
            top_memory = sorted(processes, key=lambda x: x.memory_percent, reverse=True)[:5]
            
            return {
                'total_processes': total_processes,
                'running_processes': running_processes,
                'sleeping_processes': sleeping_processes,
                'total_cpu_usage': total_cpu,
                'total_memory_usage': total_memory,
                'top_cpu_processes': [
                    {'name': p.name, 'pid': p.pid, 'cpu_percent': p.cpu_percent}
                    for p in top_cpu
                ],
                'top_memory_processes': [
                    {'name': p.name, 'pid': p.pid, 'memory_percent': p.memory_percent}
                    for p in top_memory
                ],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting system summary: {str(e)}"
            }
    
    def find_suspicious_processes(self) -> List[Dict[str, Any]]:
        """
        Find potentially suspicious processes based on criteria
        
        Returns:
            List of suspicious process information
        """
        suspicious = []
        
        try:
            processes = self.get_running_processes()
            
            for proc in processes:
                reasons = []
                
                # High CPU usage
                if proc.cpu_percent > 80:
                    reasons.append(f"High CPU usage: {proc.cpu_percent:.1f}%")
                
                # High memory usage
                if proc.memory_percent > 80:
                    reasons.append(f"High memory usage: {proc.memory_percent:.1f}%")
                
                # Suspicious names (basic heuristics)
                suspicious_names = ['temp', 'tmp', 'unknown', 'svchost', 'system']
                if any(sus in proc.name.lower() for sus in suspicious_names):
                    reasons.append(f"Suspicious name pattern: {proc.name}")
                
                # No executable path
                if not proc.exe:
                    reasons.append("No executable path")
                
                # Recently created (potential malware)
                age_hours = (time.time() - proc.create_time) / 3600
                if age_hours < 1 and proc.cpu_percent > 50:
                    reasons.append(f"Recent high-activity process: {age_hours:.1f} hours old")
                
                if reasons:
                    suspicious.append({
                        'pid': proc.pid,
                        'name': proc.name,
                        'cpu_percent': proc.cpu_percent,
                        'memory_percent': proc.memory_percent,
                        'reasons': reasons,
                        'exe': proc.exe,
                        'cmdline': proc.cmdline
                    })
        
        except Exception as e:
            print(f"Error finding suspicious processes: {str(e)}")
        
        return suspicious
    
    def kill_process_tree(self, pid: int) -> Dict[str, Any]:
        """
        Kill a process and all its children
        
        Args:
            pid: Root process PID
            
        Returns:
            Dictionary with operation result
        """
        try:
            parent = psutil.Process(pid)
            killed_processes = []
            
            # Get all children
            children = parent.children(recursive=True)
            
            # Kill children first
            for child in children:
                try:
                    child.kill()
                    killed_processes.append({
                        'pid': child.pid,
                        'name': child.name(),
                        'type': 'child'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Kill parent
            parent.kill()
            killed_processes.append({
                'pid': parent.pid,
                'name': parent.name(),
                'type': 'parent'
            })
            
            return {
                'success': True,
                'message': f"Process tree killed. Total processes: {len(killed_processes)}",
                'killed_processes': killed_processes
            }
        
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'message': f"Process not found: PID {pid}",
                'pid': pid
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error killing process tree: {str(e)}",
                'pid': pid
            }
    
    def get_process_tree(self, pid: int) -> Dict[str, Any]:
        """
        Get process tree for a given PID
        
        Args:
            pid: Process ID
            
        Returns:
            Dictionary with process tree structure
        """
        try:
            proc = psutil.Process(pid)
            
            def build_tree(process):
                try:
                    node = {
                        'pid': process.pid,
                        'name': process.name(),
                        'status': process.status(),
                        'cpu_percent': process.cpu_percent(),
                        'memory_percent': process.memory_percent(),
                        'children': []
                    }
                    
                    for child in process.children():
                        child_node = build_tree(child)
                        if child_node:
                            node['children'].append(child_node)
                    
                    return node
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return None
            
            tree = build_tree(proc)
            
            return {
                'success': True,
                'message': f"Process tree for PID {pid}",
                'tree': tree
            }
        
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'message': f"Process not found: PID {pid}",
                'pid': pid
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting process tree: {str(e)}",
                'pid': pid
            }
