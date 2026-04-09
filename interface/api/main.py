"""FastAPI backend for Ansible Labs interface"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from typing import List, Optional
import uvicorn

from interface.api.models import (
    HostInfo, GroupInfo, PlaybookInfo, ExecutionRequest, ExecutionResponse,
    ExecutionStatusResponse, LLMSuggestRequest, LLMSuggestResponse,
    LLMExplainRequest, LLMExplainResponse, ExecutionStatus
)
from interface.utils.inventory_parser import InventoryParser
from interface.utils.playbook_parser import PlaybookParser
from interface.api.ansible_runner import AnsibleRunner

app = FastAPI(title="Ansible Labs API", version="1.0.0")

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers and runner
try:
    inventory_parser = InventoryParser()
except Exception as e:
    print(f"Warning: Failed to initialize inventory parser: {e}")
    inventory_parser = None

try:
    playbook_parser = PlaybookParser()
except Exception as e:
    print(f"Warning: Failed to initialize playbook parser: {e}")
    playbook_parser = None

try:
    ansible_runner = AnsibleRunner()
except Exception as e:
    print(f"Warning: Failed to initialize ansible runner: {e}")
    ansible_runner = None

# Setup static files and templates
web_dir = Path(__file__).parent.parent / "web"
static_dir = web_dir / "static"
templates_dir = web_dir / "templates"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - serve web interface"""
    template_path = templates_dir / "index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    return HTMLResponse(content=template.render())


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}


@app.get("/api/inventory/groups", response_model=List[GroupInfo])
async def get_groups():
    """Get all groups from inventory"""
    if inventory_parser is None:
        raise HTTPException(status_code=500, detail="Inventory parser not initialized")
    try:
        data = inventory_parser.parse()
        groups = []
        for group_name, hosts in data['groups'].items():
            if not group_name.endswith(':vars'):
                group_vars = data['group_vars'].get(group_name, {})
                
                # Convert hosts to HostInfo objects, handling missing fields
                host_objects = []
                for host in hosts:
                    try:
                        # Ensure 'name' field exists
                        if 'name' not in host:
                            continue
                        host_objects.append(HostInfo(**host))
                    except Exception as e:
                        # Skip invalid hosts but log the error
                        print(f"Warning: Skipping invalid host in group {group_name}: {host}, error: {e}")
                        continue
                
                groups.append(GroupInfo(
                    name=group_name,
                    hosts=host_objects,
                    vars=group_vars if group_vars else None
                ))
        return groups
    except Exception as e:
        import traceback
        error_detail = f"Error parsing inventory: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"Error parsing inventory: {str(e)}")


@app.get("/api/inventory/hosts", response_model=List[HostInfo])
async def get_hosts(group: Optional[str] = None):
    """Get all hosts, optionally filtered by group"""
    if inventory_parser is None:
        raise HTTPException(status_code=500, detail="Inventory parser not initialized")
    try:
        if group:
            hosts = inventory_parser.get_hosts_by_group(group)
        else:
            hosts = inventory_parser.get_all_hosts()
        
        # Convert to HostInfo objects, handling missing fields
        host_objects = []
        for host in hosts:
            try:
                # Ensure 'name' field exists
                if 'name' not in host:
                    continue
                host_objects.append(HostInfo(**host))
            except Exception as e:
                # Skip invalid hosts but log the error
                print(f"Warning: Skipping invalid host: {host}, error: {e}")
                continue
        
        return host_objects
    except Exception as e:
        import traceback
        error_detail = f"Error getting hosts: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"Error getting hosts: {str(e)}")


@app.get("/api/playbooks", response_model=List[PlaybookInfo])
async def get_playbooks():
    """Get all available playbooks"""
    if playbook_parser is None:
        raise HTTPException(status_code=500, detail="Playbook parser not initialized")
    try:
        playbooks = playbook_parser.get_all_playbooks()
        return [PlaybookInfo(**pb) for pb in playbooks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting playbooks: {str(e)}")


@app.get("/api/playbooks/{playbook_name}", response_model=PlaybookInfo)
async def get_playbook(playbook_name: str):
    """Get specific playbook information"""
    try:
        playbook = playbook_parser.get_playbook_by_name(playbook_name)
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        return PlaybookInfo(**playbook)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tags", response_model=List[str])
async def get_tags():
    """Get all available tags from all playbooks"""
    if playbook_parser is None:
        raise HTTPException(status_code=500, detail="Playbook parser not initialized")
    try:
        tags = playbook_parser.get_all_tags()
        return sorted(list(tags))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tags: {str(e)}")


@app.post("/api/execute", response_model=ExecutionResponse)
async def execute_playbook(request: ExecutionRequest):
    """Execute an Ansible playbook"""
    if ansible_runner is None:
        raise HTTPException(status_code=500, detail="Ansible runner not initialized")
    try:
        execution_id = ansible_runner.execute_playbook(
            playbook=request.playbook,
            hosts=request.hosts,
            tags=request.tags,
            extra_vars=request.extra_vars,
            ask_password=request.ask_password
        )
        
        return ExecutionResponse(
            execution_id=execution_id,
            status=ExecutionStatus.RUNNING,
            playbook=request.playbook,
            hosts=request.hosts,
            tags=request.tags,
            message="Execution started"
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Playbook not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing playbook: {str(e)}")


@app.get("/api/executions/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str):
    """Get execution status"""
    execution = ansible_runner.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return ExecutionStatusResponse(
        execution_id=execution['id'],
        status=ExecutionStatus(execution['status']),
        playbook=execution['playbook'],
        hosts=execution.get('hosts'),
        tags=execution.get('tags'),
        return_code=execution.get('return_code'),
        stdout=execution.get('stdout', ''),
        stderr=execution.get('stderr', ''),
        started_at=execution.get('started_at'),
        finished_at=execution.get('finished_at')
    )


@app.get("/api/executions", response_model=List[ExecutionStatusResponse])
async def list_executions():
    """List all executions"""
    executions = ansible_runner.list_executions()
    return [
        ExecutionStatusResponse(
            execution_id=ex['id'],
            status=ExecutionStatus(ex['status']),
            playbook=ex['playbook'],
            hosts=ex.get('hosts'),
            tags=ex.get('tags'),
            return_code=ex.get('return_code'),
            started_at=ex.get('started_at'),
            finished_at=ex.get('finished_at')
        )
        for ex in executions
    ]


@app.delete("/api/executions/{execution_id}")
async def cancel_execution(execution_id: str):
    """Cancel a running execution"""
    success = ansible_runner.cancel_execution(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
    return {"message": "Execution cancelled"}


# LLM placeholder endpoints
@app.post("/api/llm/suggest", response_model=LLMSuggestResponse)
async def llm_suggest(request: LLMSuggestRequest):
    """Get LLM suggestions for playbook execution (placeholder)"""
    # Placeholder implementation
    return LLMSuggestResponse(
        suggestion="LLM integration not yet implemented. This is a placeholder endpoint.",
        confidence=0.0
    )


@app.post("/api/llm/explain", response_model=LLMExplainResponse)
async def llm_explain(request: LLMExplainRequest):
    """Get LLM explanation for playbook (placeholder)"""
    # Placeholder implementation
    playbook = playbook_parser.get_playbook_by_name(request.playbook)
    explanation = f"LLM integration not yet implemented. This is a placeholder endpoint for explaining playbook: {request.playbook}"
    
    return LLMExplainResponse(
        explanation=explanation,
        details={"playbook": playbook} if playbook else None
    )


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()

