"""Playbook selection screen for TUI"""

from textual.screen import Screen
from textual.widgets import Button, Select, Static
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from typing import List, Dict, Optional


class PlaybookSelectionScreen(Screen):
    """Screen for selecting playbook and tags"""
    
    BINDINGS = [("escape", "cancel", "Cancel")]
    
    def __init__(self, playbooks: List[Dict], tags: List[str], **kwargs):
        super().__init__(**kwargs)
        self.playbooks = playbooks
        self.tags = tags
        self.selected_playbook = None
        self.selected_tags = []
    
    def compose(self) -> ComposeResult:
        with Container(id="playbook_selection_container"):
            yield Static("Select Playbook and Tags", id="title")
            with Vertical(id="selection_area"):
                yield Static("Playbook:", classes="section_label")
                yield Select(id="playbook_select", prompt="Choose playbook...")
                yield Static("Tags (optional, use Space to select):", classes="section_label")
                yield Select(id="tags_select", prompt="Choose tags...")
                yield Static("Selected Tags:", id="selected_tags_display")
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="cancel_btn", variant="error")
                yield Button("Confirm", id="confirm_btn", variant="primary")
    
    def on_mount(self) -> None:
        """Populate selects when screen mounts"""
        playbook_select = self.query_one("#playbook_select", Select)
        tags_select = self.query_one("#tags_select", Select)
        
        # Add playbooks
        playbook_options = [(pb['name'], pb['name']) for pb in self.playbooks]
        playbook_select.set_options(playbook_options)
        
        # Add tags
        tag_options = [(tag, tag) for tag in sorted(self.tags)]
        tags_select.set_options(tag_options)
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes"""
        if event.select.id == "playbook_select":
            self.selected_playbook = event.value
        elif event.select.id == "tags_select":
            if event.value and event.value not in self.selected_tags:
                self.selected_tags.append(event.value)
                self.update_tags_display()
    
    def update_tags_display(self) -> None:
        """Update selected tags display"""
        display = self.query_one("#selected_tags_display", Static)
        if self.selected_tags:
            display.update(f"Selected Tags: {', '.join(self.selected_tags)}")
        else:
            display.update("Selected Tags: (none)")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel_btn":
            self.dismiss(None)
        elif event.button.id == "confirm_btn":
            if not self.selected_playbook:
                self.notify("Please select a playbook", severity="error")
                return
            
            result = {
                'playbook': self.selected_playbook,
                'tags': self.selected_tags if self.selected_tags else None
            }
            self.dismiss(result)


