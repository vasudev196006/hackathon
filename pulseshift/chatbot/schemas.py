from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or message text")
    topic_title: Optional[str] = Field(None, description="Current discussion topic title")
    topic_id: Optional[str] = Field(None, description="Topic unique identifier")
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chat conversation history")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Live entropy & sentiment context payload")
    conversation_id: Optional[str] = Field(None, description="Unique session conversation identifier")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Generated Markdown response")
    topic: Optional[str] = Field(None, description="Topic title evaluated")
