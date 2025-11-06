"""FastAPI backend for Ansible Labs interface - WITH BUG FIXES"""

# ... existing imports and setup code ...

# Initialize parsers and runner (lines 38-55)
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

# ... existing code ...

# BUG FIX 1: get_playbook endpoint - Added None check
@app.get("/api/playbooks/{playbook_name}", response_model=PlaybookInfo)
async def get_playbook(playbook_name: str):
    """Get specific playbook information"""
    # FIX: Check if playbook_parser is None before using it
    if playbook_parser is None:
        raise HTTPException(status_code=500, detail="Playbook parser not initialized")
    
    try:
        playbook = playbook_parser.get_playbook_by_name(playbook_name)
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        return PlaybookInfo(**playbook)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting playbook: {str(e)}")

# ... existing code ...

# BUG FIX 2: llm_explain endpoint - Added None check and error handling
@app.post("/api/llm/explain", response_model=LLMExplainResponse)
async def llm_explain(request: LLMExplainRequest):
    """Get LLM explanation for playbook (placeholder)"""
    # FIX: Check if playbook_parser is None before using it
    if playbook_parser is None:
        raise HTTPException(status_code=500, detail="Playbook parser not initialized")
    
    # FIX: Added try-except error handling like other endpoints
    try:
        playbook = playbook_parser.get_playbook_by_name(request.playbook)
        explanation = f"LLM integration not yet implemented. This is a placeholder endpoint for explaining playbook: {request.playbook}"
        
        return LLMExplainResponse(
            explanation=explanation,
            details={"playbook": playbook} if playbook else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining playbook: {str(e)}")

