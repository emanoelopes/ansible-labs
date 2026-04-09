"""Main TUI application for Ansible Labs"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import httpx
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Header, Footer
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding

from interface.tui.screens.host_selection import HostSelectionScreen
from interface.tui.screens.playbook_selection import PlaybookSelectionScreen
from interface.tui.screens.execution_view import ExecutionViewScreen


class AnsibleLabsTUI(App):
    """Main TUI application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main_container {
        padding: 1;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        margin: 1;
    }
    
    #menu_area {
        height: 60%;
        align: center middle;
    }
    
    Button {
        width: 30;
        margin: 1;
    }
    
    #status_bar {
        height: 3;
        dock: bottom;
        background: $panel;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "run_playbook", "Run Playbook"),
    ]
    
    def __init__(self, api_url: str = "http://localhost:8000", **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url
        self.api_client = httpx.AsyncClient(base_url=api_url, timeout=30.0)
        self.hosts = []
        self.groups = []
        self.playbooks = []
        self.tags = []
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_container"):
            yield Static("Ansible Labs - TUI", id="title")
            with Vertical(id="menu_area"):
                yield Button("Run Playbook", id="run_btn", variant="primary")
                yield Button("View Executions", id="executions_btn")
                yield Button("Quit", id="quit_btn", variant="error")
            yield Static("", id="status_bar")
        yield Footer()
    
    async def on_mount(self) -> None:
        """Load data when app mounts"""
        status = self.query_one("#status_bar", Static)
        status.update("Loading data...")
        
        try:
            # Load hosts and groups
            response = await self.api_client.get("/api/inventory/groups")
            self.groups = response.json()
            
            response = await self.api_client.get("/api/inventory/hosts")
            self.hosts = response.json()
            
            # Load playbooks
            response = await self.api_client.get("/api/playbooks")
            self.playbooks = response.json()
            
            # Load tags
            response = await self.api_client.get("/api/tags")
            self.tags = response.json()
            
            status.update("Ready - Press 'r' to run a playbook")
        except Exception as e:
            status.update(f"Error loading data: {e}")
    
    @on(Button.Pressed, "#run_btn")
    async def on_run_button(self) -> None:
        """Handle run playbook button"""
        await self.action_run_playbook()
    
    @on(Button.Pressed, "#executions_btn")
    async def on_executions_button(self) -> None:
        """Handle view executions button"""
        # TODO: Implement executions view
        self.notify("Executions view not yet implemented", severity="info")
    
    @on(Button.Pressed, "#quit_btn")
    def on_quit_button(self) -> None:
        """Handle quit button"""
        self.exit()
    
    async def action_run_playbook(self) -> None:
        """Run playbook workflow"""
        # Step 1: Select hosts
        host_screen = HostSelectionScreen(
            hosts=[{'name': h['name'], 'ip': h.get('ip')} for h in self.hosts],
            groups=[{'name': g['name']} for g in self.groups]
        )
        host_selection = await self.push_screen_wait(host_screen)
        
        if not host_selection:
            return
        
        # Step 2: Select playbook and tags
        playbook_screen = PlaybookSelectionScreen(
            playbooks=self.playbooks,
            tags=self.tags
        )
        playbook_selection = await self.push_screen_wait(playbook_screen)
        
        if not playbook_selection:
            return
        
        # Step 3: Execute playbook
        status = self.query_one("#status_bar", Static)
        status.update("Starting execution...")
        
        try:
            # Build hosts list
            selected_hosts = []
            if host_selection.get('groups'):
                # Get hosts from selected groups
                for group_name in host_selection['groups']:
                    group = next((g for g in self.groups if g['name'] == group_name), None)
                    if group:
                        selected_hosts.extend([h['name'] for h in group['hosts']])
            if host_selection.get('hosts'):
                selected_hosts.extend(host_selection['hosts'])
            
            # Execute
            response = await self.api_client.post(
                "/api/execute",
                json={
                    "playbook": playbook_selection['playbook'],
                    "hosts": selected_hosts if selected_hosts else None,
                    "tags": playbook_selection.get('tags'),
                    "ask_password": True
                }
            )
            
            execution_data = response.json()
            execution_id = execution_data['execution_id']
            
            # Show execution view
            execution_screen = ExecutionViewScreen(
                execution_id=execution_id,
                api_client=self.api_client
            )
            await self.push_screen_wait(execution_screen)
            
            status.update("Execution completed")
        except Exception as e:
            status.update(f"Error: {e}")
            self.notify(f"Failed to execute: {e}", severity="error")
    
    async def action_quit(self) -> None:
        """Quit application"""
        await self.api_client.aclose()
        self.exit()


def run_tui(api_url: str = "http://localhost:8000"):
    """Run the TUI application"""
    app = AnsibleLabsTUI(api_url=api_url)
    app.run()


if __name__ == "__main__":
    run_tui()


