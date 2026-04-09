"""Parser for Ansible playbook YAML files"""

import os
import re
from typing import Dict, List, Optional, Set
from pathlib import Path
import yaml


class PlaybookParser:
    """Parse Ansible playbook YAML files to extract tags and information"""
    
    def __init__(self, playbook_dir: Optional[str] = None):
        """
        Initialize parser with playbook directory
        
        Args:
            playbook_dir: Directory containing playbook files. If None, uses project root.
        """
        if playbook_dir is None:
            project_root = Path(__file__).parent.parent.parent
            playbook_dir = project_root
        
        self.playbook_dir = Path(playbook_dir)
        if not self.playbook_dir.exists():
            raise FileNotFoundError(f"Playbook directory not found: {playbook_dir}")
    
    def find_playbooks(self) -> List[Path]:
        """Find all YAML playbook files in directory"""
        playbooks = []
        for ext in ['*.yaml', '*.yml']:
            playbooks.extend(self.playbook_dir.glob(ext))
        return sorted(playbooks)
    
    def extract_tags_from_content(self, content: str) -> Set[str]:
        """Extract tags from YAML content using regex"""
        tags: Set[str] = set()
        
        # Pattern for tags: tags: tag1,tag2 or tags: [tag1, tag2] or tags: never,tag1
        tag_patterns = [
            r'tags:\s*([^\n]+)',  # Simple tags: line
            r'tags:\s*\[([^\]]+)\]',  # Tags as list
        ]
        
        for pattern in tag_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                tag_string = match.group(1).strip()
                # Split by comma and clean
                for tag in tag_string.split(','):
                    tag = tag.strip().strip('"').strip("'")
                    if tag and tag != 'never':  # Skip 'never' tag
                        tags.add(tag)
        
        return tags
    
    def parse_playbook(self, playbook_path: Path) -> Dict[str, any]:
        """
        Parse a single playbook file
        
        Args:
            playbook_path: Path to playbook file
            
        Returns:
            Dictionary with playbook information
        """
        try:
            with open(playbook_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract tags using regex (more reliable than YAML parsing for complex files)
            tags = self.extract_tags_from_content(content)
            
            # Try to parse YAML for additional info
            playbook_info: Dict[str, any] = {
                'name': playbook_path.name,
                'path': str(playbook_path),
                'tags': sorted(list(tags)),
                'description': None,
                'hosts': None
            }
            
            try:
                yaml_data = yaml.safe_load(content)
                if isinstance(yaml_data, list) and len(yaml_data) > 0:
                    first_item = yaml_data[0]
                    if isinstance(first_item, dict):
                        # Extract name/description
                        if 'name' in first_item:
                            playbook_info['description'] = first_item['name']
                        if 'hosts' in first_item:
                            playbook_info['hosts'] = first_item['hosts']
            except yaml.YAMLError:
                # If YAML parsing fails, continue with regex-extracted info
                pass
            
            return playbook_info
            
        except Exception as e:
            return {
                'name': playbook_path.name,
                'path': str(playbook_path),
                'tags': [],
                'error': str(e)
            }
    
    def get_all_playbooks(self) -> List[Dict[str, any]]:
        """Get information about all playbooks"""
        playbooks = []
        for playbook_path in self.find_playbooks():
            info = self.parse_playbook(playbook_path)
            playbooks.append(info)
        return playbooks
    
    def get_all_tags(self) -> Set[str]:
        """Get all unique tags from all playbooks"""
        all_tags: Set[str] = set()
        for playbook in self.get_all_playbooks():
            all_tags.update(playbook.get('tags', []))
        return all_tags
    
    def get_playbook_by_name(self, name: str) -> Optional[Dict[str, any]]:
        """Get playbook information by name"""
        for playbook in self.get_all_playbooks():
            if playbook['name'] == name:
                return playbook
        return None


if __name__ == "__main__":
    # Test parser
    parser = PlaybookParser()
    playbooks = parser.get_all_playbooks()
    print(f"Found {len(playbooks)} playbooks")
    print("\nFirst playbook:", playbooks[0] if playbooks else None)
    print("\nAll tags:", sorted(parser.get_all_tags()))


