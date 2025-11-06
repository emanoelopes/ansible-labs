"""Reusable TUI widgets"""

from textual.widgets import Button, Input, Select, Checkbox, Static
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult


class HostSelector(Container):
    """Widget for selecting hosts"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Select Hosts/Groups:", classes="label")
            yield Select(id="host_select", prompt="Choose hosts...")
            yield Static("Selected:", classes="label")
            yield Static("", id="selected_hosts")


class PlaybookSelector(Container):
    """Widget for selecting playbook and tags"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Select Playbook:", classes="label")
            yield Select(id="playbook_select", prompt="Choose playbook...")
            yield Static("Select Tags (optional):", classes="label")
            yield Select(id="tags_select", prompt="Choose tags...")
            yield Static("Selected Tags:", classes="label")
            yield Static("", id="selected_tags")


