"""Host selection screen for TUI"""

from textual.screen import Screen
from textual.widgets import Button, Select, Static, CheckboxList
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from typing import List, Dict


class HostSelectionScreen(Screen):
    """Screen for selecting hosts and groups"""
    
    BINDINGS = [("escape", "cancel", "Cancel")]
    
    def __init__(self, hosts: List[Dict], groups: List[Dict], **kwargs):
        super().__init__(**kwargs)
        self.hosts = hosts
        self.groups = groups
        self.selected = []
    
    def compose(self) -> ComposeResult:
        with Container(id="host_selection_container"):
            yield Static("Select Hosts or Groups", id="title")
            with Vertical(id="selection_area"):
                yield Static("Groups:", classes="section_label")
                yield CheckboxList(id="groups_list")
                yield Static("Hosts:", classes="section_label")
                yield CheckboxList(id="hosts_list")
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="cancel_btn", variant="error")
                yield Button("Confirm", id="confirm_btn", variant="primary")
    
    def on_mount(self) -> None:
        """Populate lists when screen mounts"""
        groups_list = self.query_one("#groups_list", CheckboxList)
        hosts_list = self.query_one("#hosts_list", CheckboxList)
        
        # Add groups
        group_options = [(g['name'], g['name']) for g in self.groups]
        groups_list.set_options(group_options)
        
        # Add hosts
        host_options = [(h['name'], h['name']) for h in self.hosts]
        hosts_list.set_options(host_options)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel_btn":
            self.dismiss(None)
        elif event.button.id == "confirm_btn":
            groups_list = self.query_one("#groups_list", CheckboxList)
            hosts_list = self.query_one("#hosts_list", CheckboxList)
            
            selected_groups = groups_list.selected
            selected_hosts = hosts_list.selected
            
            self.selected = {
                'groups': selected_groups,
                'hosts': selected_hosts
            }
            self.dismiss(self.selected)


