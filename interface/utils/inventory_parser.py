"""Parser for Ansible inventory.ini files"""

import os
import re
from typing import Dict, List, Optional
from pathlib import Path


class InventoryParser:
    """Parse Ansible inventory.ini files"""
    
    def __init__(self, inventory_path: Optional[str] = None):
        """
        Initialize parser with inventory file path
        
        Args:
            inventory_path: Path to inventory.ini file. If None, uses default.
        """
        if inventory_path is None:
            # Default to inventory.ini in project root
            project_root = Path(__file__).parent.parent.parent
            inventory_path = project_root / "inventory.ini"
        
        self.inventory_path = Path(inventory_path)
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"Inventory file not found: {inventory_path}")
    
    def parse(self) -> Dict[str, any]:
        """
        Parse inventory file and return structured data
        
        Returns:
            Dictionary with groups and hosts information
        """
        groups: Dict[str, List[Dict[str, str]]] = {}
        current_group: Optional[str] = None
        current_vars_group: Optional[str] = None  # Track which group's vars we're processing
        group_vars: Dict[str, Dict[str, str]] = {}
        all_hosts: List[Dict[str, str]] = []
        
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check for group definition [group_name]
                group_match = re.match(r'^\[([^\]]+)\]$', line)
                if group_match:
                    group_name = group_match.group(1)
                    
                    # Check if it's a vars section
                    if group_name.endswith(':vars'):
                        current_group = None  # Don't process hosts in vars sections
                        current_vars_group = group_name.replace(':vars', '')
                        if current_vars_group not in group_vars:
                            group_vars[current_vars_group] = {}
                    else:
                        current_group = group_name
                        current_vars_group = None
                        if current_group not in groups:
                            groups[current_group] = []
                    continue
                
                # Parse host line (only if we're in a regular group, not vars)
                if current_group and current_group in groups:
                    # Parse host definition: hostname ansible_host=ip other_vars
                    parts = line.split()
                    if parts:
                        hostname = parts[0]
                        host_info: Dict[str, str] = {'name': hostname}
                        
                        # Parse variables
                        for part in parts[1:]:
                            if '=' in part:
                                key, value = part.split('=', 1)
                                host_info[key] = value
                        
                        # Extract IP if available
                        if 'ansible_host' in host_info:
                            host_info['ip'] = host_info['ansible_host']
                        
                        groups[current_group].append(host_info)
                        all_hosts.append(host_info)
                
                # Parse group variables (when we're in a :vars section)
                elif current_vars_group is not None:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        group_vars[current_vars_group][key.strip()] = value.strip()
        
        return {
            'groups': groups,
            'all_hosts': all_hosts,
            'group_vars': group_vars
        }
    
    def get_groups(self) -> List[str]:
        """Get list of all group names"""
        data = self.parse()
        return [g for g in data['groups'].keys() if not g.endswith(':vars')]
    
    def get_hosts_by_group(self, group_name: str) -> List[Dict[str, str]]:
        """Get all hosts in a specific group"""
        data = self.parse()
        return data['groups'].get(group_name, [])
    
    def get_all_hosts(self) -> List[Dict[str, str]]:
        """Get all hosts from all groups"""
        data = self.parse()
        return data['all_hosts']
    
    def get_host_names(self) -> List[str]:
        """Get list of all host names"""
        return [host['name'] for host in self.get_all_hosts()]


if __name__ == "__main__":
    # Test parser
    parser = InventoryParser()
    data = parser.parse()
    print("Groups:", parser.get_groups())
    print("\nHosts in lab1:", parser.get_hosts_by_group('lab1')[:3])
    print("\nAll host names:", parser.get_host_names()[:5])


