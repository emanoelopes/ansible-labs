"""Wrapper for executing Ansible playbooks using ansible-runner"""

import os
import uuid
import subprocess
import threading
from typing import Dict, Optional, List, Callable
from pathlib import Path
from datetime import datetime
import json


class AnsibleRunner:
    """Wrapper for executing Ansible playbooks"""
    
    def __init__(self, project_dir: Optional[str] = None):
        """
        Initialize Ansible Runner
        
        Args:
            project_dir: Project root directory. If None, uses current directory.
        """
        if project_dir is None:
            project_dir = Path(__file__).parent.parent.parent
        self.project_dir = Path(project_dir)
        self.executions: Dict[str, Dict] = {}
        self.logs_dir = self.project_dir / "interface" / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def execute_playbook(
        self,
        playbook: str,
        hosts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        extra_vars: Optional[Dict] = None,
        ask_password: bool = True,
        callback: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """
        Execute an Ansible playbook asynchronously
        
        Args:
            playbook: Playbook file name
            hosts: List of hosts or groups
            tags: List of tags to execute
            extra_vars: Extra variables
            ask_password: Whether to ask for password
            callback: Optional callback function for real-time output (line_type, line)
            
        Returns:
            Execution ID
        """
        execution_id = str(uuid.uuid4())
        
        # Build ansible-playbook command
        cmd = ["ansible-playbook"]
        
        # Add inventory
        inventory_path = self.project_dir / "inventory.ini"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        
        # Add playbook
        playbook_path = self.project_dir / playbook
        if not playbook_path.exists():
            raise FileNotFoundError(f"Playbook not found: {playbook}")
        cmd.append(str(playbook_path))
        
        # Add hosts
        if hosts:
            cmd.extend(["-e", f"local={','.join(hosts)}"])
        
        # Add tags
        if tags:
            cmd.extend(["-t", ",".join(tags)])
        
        # Add extra vars
        if extra_vars:
            for key, value in extra_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        # Ask password flag
        if ask_password:
            cmd.append("-k")
        
        # Initialize execution record
        execution = {
            'id': execution_id,
            'playbook': playbook,
            'hosts': hosts,
            'tags': tags,
            'status': 'running',
            'cmd': ' '.join(cmd),
            'started_at': datetime.now().isoformat(),
            'return_code': None,
            'stdout': '',
            'stderr': '',
            'process': None
        }
        self.executions[execution_id] = execution
        
        # Start execution in thread
        thread = threading.Thread(
            target=self._run_playbook,
            args=(execution_id, cmd, callback),
            daemon=True
        )
        thread.start()
        
        return execution_id
    
    def _run_playbook(
        self,
        execution_id: str,
        cmd: List[str],
        callback: Optional[Callable[[str, str], None]] = None
    ):
        """Run playbook in subprocess"""
        execution = self.executions[execution_id]
        
        try:
            # Create log file
            log_file = self.logs_dir / f"{execution_id}.log"
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    cwd=str(self.project_dir)
                )
                
                execution['process'] = process
                
                # Read output line by line
                for line in iter(process.stdout.readline, ''):
                    if line:
                        execution['stdout'] += line
                        f.write(line)
                        f.flush()
                        if callback:
                            callback('stdout', line)
                
                # Wait for process to complete
                process.wait()
                execution['return_code'] = process.returncode
                
                # Read stderr
                stderr_output = process.stderr.read()
                if stderr_output:
                    execution['stderr'] = stderr_output
                    f.write(f"\n--- STDERR ---\n{stderr_output}")
                    if callback:
                        callback('stderr', stderr_output)
            
            # Update status
            if execution['return_code'] == 0:
                execution['status'] = 'success'
            else:
                execution['status'] = 'failed'
                
        except Exception as e:
            execution['status'] = 'failed'
            execution['stderr'] = str(e)
        finally:
            execution['finished_at'] = datetime.now().isoformat()
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution status by ID"""
        return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        execution = self.executions.get(execution_id)
        if execution and execution.get('process'):
            try:
                execution['process'].terminate()
                execution['status'] = 'cancelled'
                execution['finished_at'] = datetime.now().isoformat()
                return True
            except Exception:
                return False
        return False
    
    def list_executions(self) -> List[Dict]:
        """List all executions"""
        return list(self.executions.values())


