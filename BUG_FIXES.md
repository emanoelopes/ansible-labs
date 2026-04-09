# Bug Fixes for interface/api/main.py

## Bug 1: get_playbook endpoint missing None check

**Location:** `@app.get("/api/playbooks/{playbook_name}")` endpoint

**Problem:** The endpoint calls `playbook_parser.get_playbook_by_name()` without checking if `playbook_parser` is None. If initialization fails (lines 45-49), this will crash with AttributeError.

**Fix:** Add None check before using playbook_parser, similar to other endpoints like `get_playbooks()` and `get_tags()`.

**Before:**
```python
@app.get("/api/playbooks/{playbook_name}", response_model=PlaybookInfo)
async def get_playbook(playbook_name: str):
    """Get specific playbook information"""
    try:
        playbook = playbook_parser.get_playbook_by_name(playbook_name)  # ❌ No None check
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        return PlaybookInfo(**playbook)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**After:**
```python
@app.get("/api/playbooks/{playbook_name}", response_model=PlaybookInfo)
async def get_playbook(playbook_name: str):
    """Get specific playbook information"""
    if playbook_parser is None:  # ✅ Added None check
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
```

---

## Bug 2: llm_explain endpoint missing None check and error handling

**Location:** `@app.post("/api/llm/explain")` endpoint

**Problem:** 
1. The endpoint calls `playbook_parser.get_playbook_by_name()` without checking if `playbook_parser` is None.
2. The endpoint lacks try-except error handling present in other endpoints.

**Fix:** 
1. Add None check before using playbook_parser.
2. Add try-except error handling consistent with other endpoints.

**Before:**
```python
@app.post("/api/llm/explain", response_model=LLMExplainResponse)
async def llm_explain(request: LLMExplainRequest):
    """Get LLM explanation for playbook (placeholder)"""
    # ❌ No None check
    # ❌ No try-except error handling
    playbook = playbook_parser.get_playbook_by_name(request.playbook)
    explanation = f"LLM integration not yet implemented. This is a placeholder endpoint for explaining playbook: {request.playbook}"
    
    return LLMExplainResponse(
        explanation=explanation,
        details={"playbook": playbook} if playbook else None
    )
```

**After:**
```python
@app.post("/api/llm/explain", response_model=LLMExplainResponse)
async def llm_explain(request: LLMExplainRequest):
    """Get LLM explanation for playbook (placeholder)"""
    if playbook_parser is None:  # ✅ Added None check
        raise HTTPException(status_code=500, detail="Playbook parser not initialized")
    
    try:  # ✅ Added try-except error handling
        playbook = playbook_parser.get_playbook_by_name(request.playbook)
        explanation = f"LLM integration not yet implemented. This is a placeholder endpoint for explaining playbook: {request.playbook}"
        
        return LLMExplainResponse(
            explanation=explanation,
            details={"playbook": playbook} if playbook else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining playbook: {str(e)}")
```

---

## Summary

Both bugs follow the same pattern: endpoints that use `playbook_parser` without checking if it's None first. The fixes ensure:

1. **Consistency**: All endpoints that use `playbook_parser` now check for None first
2. **Error handling**: Proper error handling with descriptive messages
3. **Robustness**: The API won't crash with AttributeError if parser initialization fails

