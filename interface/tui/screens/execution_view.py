"""Execution view screen for TUI"""

from textual.screen import Screen
from textual.widgets import Button, Static, Log
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
import asyncio
from typing import Optional


class ExecutionViewScreen(Screen):
    """Screen for viewing playbook execution"""
    
    BINDINGS = [("escape", "close", "Close")]
    
    def __init__(self, execution_id: str, api_client, **kwargs):
        super().__init__(**kwargs)
        self.execution_id = execution_id
        self.api_client = api_client
        self.running = True
    
    def compose(self) -> ComposeResult:
        with Container(id="execution_container"):
            yield Static(f"Execution: {self.execution_id}", id="title")
            yield Static("Status: Running...", id="status_display")
            yield Log(id="execution_log", auto_scroll=True)
            with Horizontal(id="buttons"):
                yield Button("Cancel Execution", id="cancel_btn", variant="error")
                yield Button("Close", id="close_btn")
    
    def on_mount(self) -> None:
        """Start polling for execution updates"""
        self.set_interval(1.0, self.poll_execution)
    
    async def poll_execution(self) -> None:
        """Poll execution status and update display"""
        if not self.running:
            return
            
        log_widget = self.query_one("#execution_log", Log)
        status_display = self.query_one("#status_display", Static)
        
        try:
            response = await self.api_client.get(f"/api/executions/{self.execution_id}")
            status = response.json()
            
            # Update status
            status_text = f"Status: {status['status'].upper()}"
            if status.get('return_code') is not None:
                status_text += f" (Exit: {status['return_code']})"
            status_display.update(status_text)
            
            # Update log
            if status.get('stdout'):
                # Only show new lines
                current_output = status['stdout']
                log_widget.write(current_output)
            
            if status.get('stderr'):
                log_widget.write(f"[ERROR] {status['stderr']}")
            
            # Check if finished
            if status['status'] in ['success', 'failed', 'cancelled']:
                self.running = False
        except Exception as e:
            log_widget.write(f"[ERROR] Failed to get status: {e}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel_btn":
            # Cancel execution
            self.run_action(self.cancel_execution)
        elif event.button.id == "close_btn":
            self.running = False
            self.dismiss()
    
    async def cancel_execution(self) -> None:
        """Cancel the execution"""
        try:
            await self.api_client.delete(f"/api/executions/{self.execution_id}")
            self.notify("Execution cancelled", severity="warning")
            self.running = False
        except Exception as e:
            self.notify(f"Failed to cancel: {e}", severity="error")

