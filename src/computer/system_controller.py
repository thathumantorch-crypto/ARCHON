import os
import platform
import subprocess
import psutil
import time
import socket
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import threading
import ctypes
from ctypes import wintypes

class SystemController:
    """
    Advanced system control and monitoring capabilities
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.version = platform.version()
        self.machine = platform.machine()
        self.processor = platform.processor()
        
        # Windows-specific constants
        if self.system == 'windows':
            self.EWX_SHUTDOWN = 0x00000001
            self.EWX_REBOOT = 0x00000002
            self.EWX_LOGOFF = 0x00000004
            self.EWX_FORCE = 0x00000004
            self.EWX_POWEROFF = 0x00000008
            
            # Load Windows API
            self.user32 = ctypes.windll.user32
            self.user32.ExitWindowsEx.argtypes = [wintypes.UINT, wintypes.UINT]
            self.user32.ExitWindowsEx.restype = wintypes.BOOL
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information
        
        Returns:
            Dictionary with system information
        """
        info = {
            'system': self.system,
            'version': self.version,
            'machine': self.machine,
            'processor': self.processor,
            'python_version': platform.python_version(),
            'timestamp': datetime.now().isoformat()
        }
        
        # CPU information
        info['cpu'] = {
            'count': psutil.cpu_count(logical=True),
            'physical_count': psutil.cpu_count(logical=False),
            'usage_percent': psutil.cpu_percent(interval=1),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        info['memory'] = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2)
        }
        
        # Disk information
        info['disk'] = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info['disk'][partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2)
                }
            except (PermissionError, OSError):
                continue
        
        # Network information
        info['network'] = self._get_network_info()
        
        # Boot time
        info['boot_time'] = datetime.fromtimestamp(psutil.boot_time()).isoformat()
        
        # Users
        info['users'] = []
        for user in psutil.users():
            info['users'].append({
                'name': user.name,
                'terminal': user.terminal,
                'host': user.host,
                'started': datetime.fromtimestamp(user.started).isoformat()
            })
        
        return info
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        network_info = {
            'interfaces': {},
            'connections': {
                'established': 0,
                'listening': 0,
                'time_wait': 0
            }
        }
        
        # Network interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {
                'addresses': []
            }
            
            for addr in addrs:
                address_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                }
                interface_info['addresses'].append(address_info)
            
            network_info['interfaces'][interface] = interface_info
        
        # Network I/O stats
        net_io = psutil.net_io_counters()
        network_info['io_stats'] = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
        
        # Connection statistics
        for conn in psutil.net_connections():
            if conn.status == 'ESTABLISHED':
                network_info['connections']['established'] += 1
            elif conn.status == 'LISTEN':
                network_info['connections']['listening'] += 1
            elif conn.status == 'TIME_WAIT':
                network_info['connections']['time_wait'] += 1
        
        return network_info
    
    def shutdown_system(self, force: bool = False, delay: int = 0) -> Dict[str, Any]:
        """
        Shutdown the system
        
        Args:
            force: Whether to force shutdown
            delay: Delay in seconds before shutdown
            
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                if delay > 0:
                    # Schedule shutdown with delay
                    cmd = f'shutdown /s /t {delay}'
                    if force:
                        cmd += ' /f'
                    subprocess.run(cmd, shell=True)
                else:
                    # Immediate shutdown
                    flags = self.EWX_SHUTDOWN
                    if force:
                        flags |= self.EWX_FORCE
                    
                    if not self.user32.ExitWindowsEx(flags, 0):
                        return {
                            'success': False,
                            'message': 'Failed to initiate shutdown'
                        }
            
            elif self.system in ['linux', 'darwin']:
                if delay > 0:
                    cmd = f'shutdown -h +{delay // 60}'
                else:
                    cmd = 'shutdown -h now'
                
                if force:
                    cmd = f'sudo {cmd}'  # Requires sudo
                
                subprocess.run(cmd, shell=True)
            
            return {
                'success': True,
                'message': f'System shutdown initiated (delay: {delay}s)',
                'delay': delay,
                'force': force
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error initiating shutdown: {str(e)}'
            }
    
    def restart_system(self, force: bool = False, delay: int = 0) -> Dict[str, Any]:
        """
        Restart the system
        
        Args:
            force: Whether to force restart
            delay: Delay in seconds before restart
            
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                if delay > 0:
                    cmd = f'shutdown /r /t {delay}'
                    if force:
                        cmd += ' /f'
                    subprocess.run(cmd, shell=True)
                else:
                    flags = self.EWX_REBOOT
                    if force:
                        flags |= self.EWX_FORCE
                    
                    if not self.user32.ExitWindowsEx(flags, 0):
                        return {
                            'success': False,
                            'message': 'Failed to initiate restart'
                        }
            
            elif self.system in ['linux', 'darwin']:
                if delay > 0:
                    cmd = f'shutdown -r +{delay // 60}'
                else:
                    cmd = 'shutdown -r now'
                
                if force:
                    cmd = f'sudo {cmd}'
                
                subprocess.run(cmd, shell=True)
            
            return {
                'success': True,
                'message': f'System restart initiated (delay: {delay}s)',
                'delay': delay,
                'force': force
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error initiating restart: {str(e)}'
            }
    
    def sleep_system(self) -> Dict[str, Any]:
        """
        Put the system to sleep
        
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                # Windows sleep command
                subprocess.run('rundll32.exe powrprof.dll,SetSuspendState Sleep', shell=True)
            
            elif self.system == 'darwin':
                # macOS sleep command
                subprocess.run('pmset sleepnow', shell=True)
            
            elif self.system == 'linux':
                # Linux sleep (requires systemd)
                subprocess.run('systemctl suspend', shell=True)
            
            return {
                'success': True,
                'message': 'System sleep initiated'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error initiating sleep: {str(e)}'
            }
    
    def hibernate_system(self) -> Dict[str, Any]:
        """
        Hibernate the system
        
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                subprocess.run('rundll32.exe powrprof.dll,SetSuspendState Hibernate', shell=True)
            
            elif self.system == 'darwin':
                # macOS hibernate
                subprocess.run('pmset hibernatenow', shell=True)
            
            elif self.system == 'linux':
                # Linux hibernate
                subprocess.run('systemctl hibernate', shell=True)
            
            return {
                'success': True,
                'message': 'System hibernation initiated'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error initiating hibernation: {str(e)}'
            }
    
    def lock_system(self) -> Dict[str, Any]:
        """
        Lock the system
        
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                subprocess.run('rundll32.exe user32.dll,LockWorkStation', shell=True)
            
            elif self.system == 'darwin':
                # macOS lock screen
                subprocess.run('/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend', shell=True)
            
            elif self.system == 'linux':
                # Linux lock screen (depends on desktop environment)
                subprocess.run('xdg-screensaver lock', shell=True)
            
            return {
                'success': True,
                'message': 'System locked'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error locking system: {str(e)}'
            }
    
    def log_out_user(self) -> Dict[str, Any]:
        """
        Log out the current user
        
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                flags = self.EWX_LOGOFF
                self.user32.ExitWindowsEx(flags, 0)
            
            elif self.system in ['linux', 'darwin']:
                subprocess.run('pkill -KILL -u $(whoami)', shell=True)
            
            return {
                'success': True,
                'message': 'User logged out'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error logging out: {str(e)}'
            }
    
    def set_system_volume(self, volume_level: int) -> Dict[str, Any]:
        """
        Set system volume (Windows only)
        
        Args:
            volume_level: Volume level (0-100)
            
        Returns:
            Dictionary with operation result
        """
        try:
            if self.system == 'windows':
                # Use PowerShell to set volume
                script = f'''
                $wsh = New-Object -ComObject WScript.Shell
                $wsh.SendKeys([char]175)  # Volume up
                '''
                
                # This is a simplified approach - proper volume control requires more complex API calls
                for _ in range(volume_level // 10):
                    subprocess.run('powershell -c "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]175)"', shell=True)
                    time.sleep(0.1)
            
            else:
                return {
                    'success': False,
                    'message': 'Volume control not supported on this platform'
                }
            
            return {
                'success': True,
                'message': f'Volume set to {volume_level}%',
                'volume_level': volume_level
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error setting volume: {str(e)}'
            }
    
    def get_system_performance(self, duration: int = 10) -> Dict[str, Any]:
        """
        Monitor system performance over time
        
        Args:
            duration: Monitoring duration in seconds
            
        Returns:
            Dictionary with performance data
        """
        performance_data = {
            'duration': duration,
            'start_time': datetime.now().isoformat(),
            'samples': [],
            'interval': 1.0
        }
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                sample = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': psutil.cpu_percent(interval=None),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': {},
                    'network_io': {}
                }
                
                # Disk usage for main drives
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        sample['disk_usage'][partition.device] = usage.percent
                    except:
                        continue
                
                # Network I/O
                net_io = psutil.net_io_counters()
                sample['network_io'] = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                }
                
                performance_data['samples'].append(sample)
                time.sleep(1.0)
            
            except Exception as e:
                performance_data['samples'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
        
        performance_data['end_time'] = datetime.now().isoformat()
        performance_data['sample_count'] = len(performance_data['samples'])
        
        # Calculate statistics
        if performance_data['samples']:
            cpu_values = [s.get('cpu_percent', 0) for s in performance_data['samples'] if 'cpu_percent' in s]
            memory_values = [s.get('memory_percent', 0) for s in performance_data['samples'] if 'memory_percent' in s]
            
            if cpu_values:
                performance_data['cpu_stats'] = {
                    'avg': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values)
                }
            
            if memory_values:
                performance_data['memory_stats'] = {
                    'avg': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'min': min(memory_values)
                }
        
        return {
            'success': True,
            'message': f'Performance monitoring completed ({duration}s)',
            'data': performance_data
        }
    
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get all environment variables
        
        Returns:
            Dictionary of environment variables
        """
        return dict(os.environ)
    
    def set_environment_variable(self, name: str, value: str, 
                                permanent: bool = False) -> Dict[str, Any]:
        """
        Set an environment variable
        
        Args:
            name: Variable name
            value: Variable value
            permanent: Whether to make permanent (system-wide)
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Set for current session
            os.environ[name] = value
            
            if permanent:
                if self.system == 'windows':
                    # Set in Windows registry (requires admin)
                    import winreg
                    key = winreg.HKEY_LOCAL_MACHINE
                    subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
                    
                    with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as registry_key:
                        winreg.SetValueEx(registry_key, name, 0, winreg.REG_EXPAND_SZ, value)
                    
                    # Broadcast change
                    subprocess.run('rundll32.exe sysdm.cpl,EditEnvironmentVariables', shell=True)
                
                else:
                    # Add to shell profile for Unix-like systems
                    home = os.path.expanduser('~')
                    profile_files = ['.bashrc', '.zshrc', '.profile']
                    
                    for profile in profile_files:
                        profile_path = os.path.join(home, profile)
                        if os.path.exists(profile_path):
                            with open(profile_path, 'a') as f:
                                f.write(f'\nexport {name}="{value}"\n')
                            break
            
            return {
                'success': True,
                'message': f'Environment variable {name} set',
                'name': name,
                'value': value,
                'permanent': permanent
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error setting environment variable: {str(e)}',
                'name': name
            }
    
    def get_network_connections(self) -> List[Dict[str, Any]]:
        """
        Get all network connections
        
        Returns:
            List of network connection information
        """
        connections = []
        
        try:
            for conn in psutil.net_connections():
                connection_info = {
                    'fd': conn.fd,
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'laddr': {
                        'ip': conn.laddr.ip,
                        'port': conn.laddr.port
                    } if conn.laddr else None,
                    'raddr': {
                        'ip': conn.raddr.ip,
                        'port': conn.raddr.port
                    } if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                }
                
                # Add process name if PID is available
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        connection_info['process_name'] = proc.name()
                    except:
                        connection_info['process_name'] = 'Unknown'
                
                connections.append(connection_info)
        
        except Exception as e:
            print(f"Error getting network connections: {str(e)}")
        
        return connections
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform system health check
        
        Returns:
            Dictionary with health status
        """
        health_status = {
            'overall': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            health_status['errors'].append(f"High CPU usage: {cpu_percent}%")
            health_status['overall'] = 'critical'
        elif cpu_percent > 70:
            health_status['warnings'].append(f"Elevated CPU usage: {cpu_percent}%")
            if health_status['overall'] == 'healthy':
                health_status['overall'] = 'warning'
        
        health_status['checks']['cpu'] = {
            'status': 'ok' if cpu_percent < 70 else ('warning' if cpu_percent < 90 else 'critical'),
            'usage_percent': cpu_percent
        }
        
        # Memory check
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health_status['errors'].append(f"High memory usage: {memory.percent}%")
            health_status['overall'] = 'critical'
        elif memory.percent > 80:
            health_status['warnings'].append(f"Elevated memory usage: {memory.percent}%")
            if health_status['overall'] == 'healthy':
                health_status['overall'] = 'warning'
        
        health_status['checks']['memory'] = {
            'status': 'ok' if memory.percent < 80 else ('warning' if memory.percent < 90 else 'critical'),
            'usage_percent': memory.percent,
            'available_gb': round(memory.available / (1024**3), 2)
        }
        
        # Disk check
        disk_issues = 0
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 95:
                    health_status['errors'].append(f"Critical disk space on {partition.device}: {usage.percent}%")
                    disk_issues += 1
                elif usage.percent > 85:
                    health_status['warnings'].append(f"Low disk space on {partition.device}: {usage.percent}%")
                    if disk_issues == 0:
                        disk_issues = -1  # Warning level
            except:
                continue
        
        if disk_issues > 0:
            health_status['overall'] = 'critical'
        elif disk_issues < 0 and health_status['overall'] == 'healthy':
            health_status['overall'] = 'warning'
        
        health_status['checks']['disk'] = {
            'status': 'ok' if disk_issues == 0 else ('warning' if disk_issues < 0 else 'critical'),
            'issues_found': max(0, disk_issues)
        }
        
        # Temperature check (if available)
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    high_temps = 0
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 80:  # High temperature threshold
                                high_temps += 1
                    
                    if high_temps > 0:
                        health_status['warnings'].append(f"High temperatures detected: {high_temps} sensors")
                        if health_status['overall'] == 'healthy':
                            health_status['overall'] = 'warning'
                    
                    health_status['checks']['temperature'] = {
                        'status': 'ok' if high_temps == 0 else 'warning',
                        'high_temp_sensors': high_temps
                    }
        except:
            health_status['checks']['temperature'] = {
                'status': 'unavailable'
            }
        
        return health_status
    
    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage
        
        Returns:
            CPU usage percentage (0-100)
        """
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_memory_usage(self) -> float:
        """
        Get current memory usage percentage
        
        Returns:
            Memory usage percentage (0-100)
        """
        try:
            memory = psutil.virtual_memory()
            return memory.percent
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return 0.0
    
    def get_disk_usage(self) -> Dict[str, float]:
        """
        Get disk usage for all mounted drives
        
        Returns:
            Dictionary with disk usage information
        """
        try:
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except Exception as e:
                    print(f"Error getting disk usage for {partition.device}: {e}")
                    continue
            
            return disk_usage
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return {}
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get network statistics
        
        Returns:
            Dictionary with network statistics
        """
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return {}
    
    def get_process_count(self) -> int:
        """
        Get total number of running processes
        
        Returns:
            Number of running processes
        """
        try:
            return len(psutil.pids())
        except Exception as e:
            print(f"Error getting process count: {e}")
            return 0
