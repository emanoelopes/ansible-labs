"""Pydantic models for API requests and responses"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HostInfo(BaseModel):
    """Host information model"""
    name: str
    ip: Optional[str] = None
    group: Optional[str] = None
    ansible_host: Optional[str] = None


class GroupInfo(BaseModel):
    """Group information model"""
    name: str
    hosts: List[HostInfo]
    vars: Optional[Dict[str, str]] = None


class PlaybookInfo(BaseModel):
    """Playbook information model"""
    name: str
    path: str
    description: Optional[str] = None
    tags: List[str] = []
    hosts: Optional[str] = None


class ExecutionRequest(BaseModel):
    """Request model for executing a playbook"""
    playbook: str = Field(..., description="Playbook file name")
    hosts: Optional[List[str]] = Field(None, description="List of host names or groups")
    tags: Optional[List[str]] = Field(None, description="List of tags to execute")
    extra_vars: Optional[Dict[str, Any]] = Field(None, description="Extra variables")
    ask_password: bool = Field(True, description="Ask for password (-k flag)")


class ExecutionResponse(BaseModel):
    """Response model for execution"""
    execution_id: str
    status: ExecutionStatus
    playbook: str
    hosts: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    message: Optional[str] = None


class ExecutionStatusResponse(BaseModel):
    """Response model for execution status"""
    execution_id: str
    status: ExecutionStatus
    playbook: str
    hosts: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    return_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class LLMSuggestRequest(BaseModel):
    """Request model for LLM suggestions (placeholder)"""
    context: Optional[str] = Field(None, description="Context for suggestion")
    playbook: Optional[str] = Field(None, description="Playbook name")
    hosts: Optional[List[str]] = Field(None, description="Selected hosts")


class LLMSuggestResponse(BaseModel):
    """Response model for LLM suggestions (placeholder)"""
    suggestion: str
    confidence: Optional[float] = None


class LLMExplainRequest(BaseModel):
    """Request model for LLM explanations (placeholder)"""
    playbook: str = Field(..., description="Playbook to explain")
    task: Optional[str] = Field(None, description="Specific task to explain")


class LLMExplainResponse(BaseModel):
    """Response model for LLM explanations (placeholder)"""
    explanation: str
    details: Optional[Dict[str, Any]] = None


